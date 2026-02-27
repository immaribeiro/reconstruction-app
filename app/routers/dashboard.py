from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ..database import get_db # Use get_db for SQLAlchemy sessions
from ..models import Reminder, FoodLog, TrainingLog, MentalLog, DailySummary, CostCategory, CostArticle, CostTransaction
from ..auth import get_api_key

from sqlalchemy.orm import Session # Import Session from SQLAlchemy
from sqlalchemy import select # Import select for building queries

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_api_key)])

# Pydantic models for response data
class TodayDashboardResponse(BaseModel):
    date: date
    reminders: List["ReminderRead"]
    food: List["FoodLogRead"]
    training: List["TrainingLogRead"]
    mental: List["MentalLogRead"]
    summary: Optional["DailySummaryRead"]
    costs_summary: dict

class WeekDashboardResponse(BaseModel):
    start_of_week: date
    end_of_week: date
    total_spent_week: float

# Import Read models (defined in their respective router files)
from .costs import CostCategoryRead, CostArticleRead, CostTransactionRead
from .reminders import ReminderRead
from .food import FoodLogRead
from .training import TrainingLogRead
from .mental import MentalLogRead
from .summary import DailySummaryRead


@router.get("/today", response_model=TodayDashboardResponse)
def get_today_dashboard_data(db: Session = Depends(get_db)):
    today = date.today()

    reminders = db.query(Reminder).filter(Reminder.status == "pending").all()
    food_logs = db.query(FoodLog).filter(FoodLog.logged_at >= datetime.combine(today, datetime.min.time())).all()
    training_logs = db.query(TrainingLog).filter(TrainingLog.logged_at >= datetime.combine(today, datetime.min.time())).all()
    mental_logs = db.query(MentalLog).filter(MentalLog.logged_at >= datetime.combine(today, datetime.min.time())).all()
    daily_summary = db.query(DailySummary).filter(DailySummary.entry_date == today).first()

    # Costs Summary (Example aggregation)
    total_spent_today = db.query(CostTransaction.amount).filter(CostTransaction.transaction_date == today).all()
    total_spent_today_sum = sum([t[0] for t in total_spent_today]) if total_spent_today else 0

    return {
        "date": today,
        "reminders": [ReminderRead.model_validate(r) for r in reminders],
        "food": [FoodLogRead.model_validate(f) for f in food_logs],
        "training": [TrainingLogRead.model_validate(t) for t in training_logs],
        "mental": [MentalLogRead.model_validate(m) for m in mental_logs],
        "summary": DailySummaryRead.model_validate(daily_summary) if daily_summary else None,
        "costs_summary": {
            "total_spent_today": total_spent_today_sum,
            # Add more cost aggregates as needed (e.g., by category, remaining budget)
        }
    }

# Example for a weekly overview
@router.get("/week", response_model=WeekDashboardResponse)
def get_week_dashboard_data(db: Session = Depends(get_db)):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) # Monday as start of week
    end_of_week = start_of_week + timedelta(days=6)

    # Example: total spent this week
    total_spent_week = db.query(CostTransaction.amount).filter(
        CostTransaction.transaction_date >= start_of_week,
        CostTransaction.transaction_date <= end_of_week
    ).all()
    total_spent_week_sum = sum([t[0] for t in total_spent_week]) if total_spent_week else 0

    return {
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "total_spent_week": total_spent_week_sum,
        # Add more weekly aggregates as needed
    }