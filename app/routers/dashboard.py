from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import CostCategory, CostArticle, CostTransaction, Reminder
from ..auth import get_api_key

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_api_key)])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    """Main dashboard data — totals, per-category breakdown, recent transactions."""
    categories = db.query(CostCategory).all()

    category_data = []
    grand_total = 0.0
    grand_invoiced = 0.0

    for cat in categories:
        cat_total = 0.0
        cat_invoiced = 0.0
        for art in cat.articles:
            for txn in art.transactions:
                cat_total += txn.amount
                if txn.has_invoice:
                    cat_invoiced += txn.amount
        category_data.append({
            "id": cat.id,
            "name": cat.name,
            "budgeted": cat.budgeted_total,
            "spent": round(cat_total, 2),
            "invoiced": round(cat_invoiced, 2),
            "articles": len(cat.articles),
        })
        grand_total += cat_total
        grand_invoiced += cat_invoiced

    # Recent transactions
    recent = db.query(CostTransaction).order_by(CostTransaction.created_at.desc()).limit(10).all()
    recent_data = []
    for txn in recent:
        recent_data.append({
            "id": txn.id,
            "date": str(txn.transaction_date),
            "amount": txn.amount,
            "payment_method": txn.payment_method,
            "has_invoice": txn.has_invoice,
            "article": txn.article.name,
            "category": txn.article.category.name,
        })

    # Pending reminders
    pending = db.query(Reminder).filter(Reminder.status == "pending").count()

    return {
        "total_spent": round(grand_total, 2),
        "total_invoiced": round(grand_invoiced, 2),
        "total_not_invoiced": round(grand_total - grand_invoiced, 2),
        "pending_reminders": pending,
        "categories": category_data,
        "recent_transactions": recent_data,
    }
