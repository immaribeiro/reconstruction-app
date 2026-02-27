from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel # For API Request/Response Models

from ..database import get_db # Use get_db for SQLAlchemy sessions
from ..models import CostCategory, CostArticle, CostTransaction # SQLAlchemy ORM models
from ..auth import get_api_key

from sqlalchemy.orm import Session # Import Session from SQLAlchemy

router = APIRouter(prefix="/costs", tags=["costs"], dependencies=[Depends(get_api_key)])

# --- Pydantic models for requests and responses (using BaseModel for validation) ---
# Cost Category
class CostCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CostCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CostCategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config: # Pydantic configuration to enable orm_mode
        from_attributes = True

class CostCategoryReadWithArticles(CostCategoryRead):
    articles: List["CostArticleRead"] = [] # Forward reference

class CostArticleRead(BaseModel):
    id: int
    category_id: int
    name: str
    total_budgeted_amount: Optional[float] = None

    class Config:
        from_attributes = True

class CostArticleReadWithTransactions(CostArticleRead):
    transactions: List["CostTransactionRead"] = [] # Forward reference

# Cost Transaction
class CostTransactionCreate(BaseModel):
    article_id: int
    transaction_date: date
    phase_number: Optional[int] = None
    payment_method: str
    amount: float
    has_invoice: bool
    notes: Optional[str] = None

class CostTransactionUpdate(BaseModel):
    article_id: Optional[int] = None
    transaction_date: Optional[date] = None
    phase_number: Optional[int] = None
    payment_method: Optional[str] = None
    amount: Optional[float] = None
    has_invoice: Optional[bool] = None
    notes: Optional[str] = None

class CostTransactionRead(BaseModel):
    id: int
    article_id: int
    transaction_date: date
    phase_number: Optional[int] = None
    payment_method: str
    amount: float
    has_invoice: bool
    notes: Optional[str] = None
    created_datetime: datetime

    class Config:
        from_attributes = True

class CostTransactionReadWithArticle(CostTransactionRead):
    article: Optional[CostArticleRead] = None


# --- Cost Categories Endpoints ---
@router.post("/categories", response_model=CostCategoryRead, status_code=status.HTTP_201_CREATED)
def create_cost_category(category: CostCategoryCreate, db: Session = Depends(get_db)):
    db_category = CostCategory(**category.model_dump()) # Create instance directly
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CostCategoryReadWithArticles])
def get_cost_categories(db: Session = Depends(get_db)):
    categories = db.query(CostCategory).all()
    return categories

@router.get("/categories/{category_id}", response_model=CostCategoryReadWithArticles)
def get_cost_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(CostCategory).filter(CostCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostCategory not found")
    return category

@router.patch("/categories/{category_id}", response_model=CostCategoryRead)
def update_cost_category(category_id: int, category: CostCategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(CostCategory).filter(CostCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostCategory not found")
    
    category_data = category.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cost_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(CostCategory).filter(CostCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostCategory not found")
    
    articles_in_category = db.query(CostArticle).filter(CostArticle.category_id == category_id).first()
    if articles_in_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete category with associated articles")

    db.delete(db_category)
    db.commit()
    return {"ok": True}

# --- Cost Articles Endpoints ---
@router.post("/articles", response_model=CostArticleRead, status_code=status.HTTP_201_CREATED)
def create_cost_article(article: CostArticleCreate, db: Session = Depends(get_db)):
    # Check if category_id exists
    category = db.query(CostCategory).filter(CostCategory.id == article.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostCategory not found")
    
    db_article = CostArticle(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.get("/articles", response_model=List[CostArticleReadWithTransactions])
def get_cost_articles(db: Session = Depends(get_db), category_id: Optional[int] = None):
    query = db.query(CostArticle)
    if category_id:
        query = query.filter(CostArticle.category_id == category_id)
    articles = query.all()
    return articles

@router.get("/articles/{article_id}", response_model=CostArticleReadWithTransactions)
def get_cost_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(CostArticle).filter(CostArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostArticle not found")
    return article

@router.patch("/articles/{article_id}", response_model=CostArticleRead)
def update_cost_article(article_id: int, article: CostArticleUpdate, db: Session = Depends(get_db)):
    db_article = db.query(CostArticle).filter(CostArticle.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostArticle not found")
    
    if article.category_id:
        category = db.query(CostCategory).filter(CostCategory.id == article.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostCategory not found")

    article_data = article.model_dump(exclude_unset=True)
    for key, value in article_data.items():
        setattr(db_article, key, value)
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cost_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(CostArticle).filter(CostArticle.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostArticle not found")
    
    transactions_in_article = db.query(CostTransaction).filter(CostTransaction.article_id == article_id).first()
    if transactions_in_article:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete article with associated transactions")

    db.delete(db_article)
    db.commit()
    return {"ok": True}

# --- Cost Transactions Endpoints ---
@router.post("/transactions", response_model=CostTransactionRead, status_code=status.HTTP_201_CREATED)
def create_cost_transaction(transaction: CostTransactionCreate, db: Session = Depends(get_db)):
    # Check if article_id exists
    article = db.query(CostArticle).filter(CostArticle.id == transaction.article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostArticle not found")

    db_transaction = CostTransaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/transactions", response_model=List[CostTransactionReadWithArticle])
def get_cost_transactions(
    db: Session = Depends(get_db),
    article_id: Optional[int] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to")
):
    query = db.query(CostTransaction)
    if article_id:
        query = query.filter(CostTransaction.article_id == article_id)
    if from_date:
        query = query.filter(CostTransaction.transaction_date >= from_date)
    if to_date:
        query = query.filter(CostTransaction.transaction_date <= to_date)
    
    transactions = query.all()
    return transactions

@router.get("/transactions/{transaction_id}", response_model=CostTransactionReadWithArticle)
def get_cost_transaction_by_id(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(CostTransaction).filter(CostTransaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostTransaction not found")
    return transaction

@router.patch("/transactions/{transaction_id}", response_model=CostTransactionRead)
def update_cost_transaction(transaction_id: int, transaction: CostTransactionUpdate, db: Session = Depends(get_db)):
    db_transaction = db.query(CostTransaction).filter(CostTransaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostTransaction not found")
    
    if transaction.article_id:
        article = db.query(CostArticle).filter(CostArticle.id == transaction.article_id).first()
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostArticle not found")

    transaction_data = transaction.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        # Prevent created_datetime from being updated
        if key == "created_datetime":
            continue
        setattr(db_transaction, key, value)
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cost_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = db.query(CostTransaction).filter(CostTransaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CostTransaction not found")
    
    db.delete(db_transaction)
    db.commit()
    return {"ok": True}