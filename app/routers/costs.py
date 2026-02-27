from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CostCategory, CostArticle, CostTransaction
from ..auth import get_api_key

router = APIRouter(prefix="/costs", tags=["costs"], dependencies=[Depends(get_api_key)])


# --- Pydantic schemas ---
class CostCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    budgeted_total: Optional[float] = None

class CostCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    budgeted_total: Optional[float] = None

class CostTransactionRead(BaseModel):
    id: int
    article_id: int
    transaction_date: date
    phase_number: Optional[int] = None
    payment_method: str
    amount: float
    has_invoice: bool
    notes: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class CostArticleRead(BaseModel):
    id: int
    category_id: int
    name: str
    budgeted_amount: Optional[float] = None
    notes: Optional[str] = None
    transactions: List[CostTransactionRead] = []
    class Config:
        from_attributes = True

class CostCategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    budgeted_total: Optional[float] = None
    articles: List[CostArticleRead] = []
    class Config:
        from_attributes = True

class CostArticleCreate(BaseModel):
    category_id: int
    name: str
    budgeted_amount: Optional[float] = None
    notes: Optional[str] = None

class CostArticleUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    budgeted_amount: Optional[float] = None
    notes: Optional[str] = None

class CostTransactionCreate(BaseModel):
    article_id: int
    transaction_date: date
    phase_number: Optional[int] = None
    payment_method: str
    amount: float
    has_invoice: bool = False
    notes: Optional[str] = None

class CostTransactionUpdate(BaseModel):
    article_id: Optional[int] = None
    transaction_date: Optional[date] = None
    phase_number: Optional[int] = None
    payment_method: Optional[str] = None
    amount: Optional[float] = None
    has_invoice: Optional[bool] = None
    notes: Optional[str] = None


# --- Categories ---
@router.post("/categories", response_model=CostCategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data: CostCategoryCreate, db: Session = Depends(get_db)):
    cat = CostCategory(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/categories", response_model=List[CostCategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(CostCategory).all()

@router.get("/categories/{cat_id}", response_model=CostCategoryRead)
def get_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(CostCategory).filter(CostCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.patch("/categories/{cat_id}", response_model=CostCategoryRead)
def update_category(cat_id: int, data: CostCategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(CostCategory).filter(CostCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/categories/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(CostCategory).filter(CostCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()


# --- Articles ---
@router.post("/articles", response_model=CostArticleRead, status_code=status.HTTP_201_CREATED)
def create_article(data: CostArticleCreate, db: Session = Depends(get_db)):
    if not db.query(CostCategory).filter(CostCategory.id == data.category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")
    art = CostArticle(**data.model_dump())
    db.add(art)
    db.commit()
    db.refresh(art)
    return art

@router.get("/articles", response_model=List[CostArticleRead])
def list_articles(db: Session = Depends(get_db), category_id: Optional[int] = None):
    q = db.query(CostArticle)
    if category_id:
        q = q.filter(CostArticle.category_id == category_id)
    return q.all()

@router.patch("/articles/{art_id}", response_model=CostArticleRead)
def update_article(art_id: int, data: CostArticleUpdate, db: Session = Depends(get_db)):
    art = db.query(CostArticle).filter(CostArticle.id == art_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(art, k, v)
    db.commit()
    db.refresh(art)
    return art

@router.delete("/articles/{art_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(art_id: int, db: Session = Depends(get_db)):
    art = db.query(CostArticle).filter(CostArticle.id == art_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(art)
    db.commit()


# --- Transactions ---
@router.post("/transactions", response_model=CostTransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(data: CostTransactionCreate, db: Session = Depends(get_db)):
    if not db.query(CostArticle).filter(CostArticle.id == data.article_id).first():
        raise HTTPException(status_code=404, detail="Article not found")
    txn = CostTransaction(**data.model_dump())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

@router.get("/transactions", response_model=List[CostTransactionRead])
def list_transactions(
    db: Session = Depends(get_db),
    article_id: Optional[int] = None,
    category_id: Optional[int] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    q = db.query(CostTransaction)
    if article_id:
        q = q.filter(CostTransaction.article_id == article_id)
    if category_id:
        q = q.join(CostArticle).filter(CostArticle.category_id == category_id)
    if from_date:
        q = q.filter(CostTransaction.transaction_date >= from_date)
    if to_date:
        q = q.filter(CostTransaction.transaction_date <= to_date)
    return q.all()

@router.patch("/transactions/{txn_id}", response_model=CostTransactionRead)
def update_transaction(txn_id: int, data: CostTransactionUpdate, db: Session = Depends(get_db)):
    txn = db.query(CostTransaction).filter(CostTransaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(txn, k, v)
    db.commit()
    db.refresh(txn)
    return txn

@router.delete("/transactions/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(CostTransaction).filter(CostTransaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()


# --- Summary ---
class CategorySummary(BaseModel):
    id: int
    name: str
    budgeted_total: Optional[float]
    total_spent: float
    article_count: int
    transaction_count: int

class OverallSummary(BaseModel):
    total_budgeted: float
    total_spent: float
    total_with_invoice: float
    total_without_invoice: float
    categories: List[CategorySummary]

@router.get("/summary", response_model=OverallSummary)
def get_summary(db: Session = Depends(get_db)):
    categories = db.query(CostCategory).all()
    cat_summaries = []
    total_budgeted = 0.0
    total_spent = 0.0
    total_invoice = 0.0
    total_no_invoice = 0.0

    for cat in categories:
        cat_spent = 0.0
        txn_count = 0
        for art in cat.articles:
            for txn in art.transactions:
                cat_spent += txn.amount
                txn_count += 1
                if txn.has_invoice:
                    total_invoice += txn.amount
                else:
                    total_no_invoice += txn.amount
        cat_summaries.append(CategorySummary(
            id=cat.id,
            name=cat.name,
            budgeted_total=cat.budgeted_total,
            total_spent=cat_spent,
            article_count=len(cat.articles),
            transaction_count=txn_count,
        ))
        total_spent += cat_spent
        if cat.budgeted_total:
            total_budgeted += cat.budgeted_total

    return OverallSummary(
        total_budgeted=total_budgeted,
        total_spent=total_spent,
        total_with_invoice=total_invoice,
        total_without_invoice=total_no_invoice,
        categories=cat_summaries,
    )
