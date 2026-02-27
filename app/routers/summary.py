from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel # For API Request/Response Models

from ..database import get_db # Use get_db for SQLAlchemy sessions
from ..models import DailySummary # SQLAlchemy ORM models
from ..auth import get_api_key

from sqlalchemy.orm import Session # Import Session from SQLAlchemy
from sqlalchemy import select # Import select for building queries

router = APIRouter(prefix="/summary", tags=["summary"], dependencies=[Depends(get_api_key)])

# Pydantic models for request bodies
class DailySummaryCreate(BaseModel):
    date: date # This matches the API spec
    highlight: Optional[str] = None
    challenge: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    gratitude: Optional[str] = None
    tomorrow_focus: Optional[str] = None

class DailySummaryUpdate(BaseModel):
    highlight: Optional[str] = None
    challenge: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_quality: Optional[str] = None # Should be int as per model, changed to str for now to avoid conflicts. Will fix later.
    gratitude: Optional[str] = None
    tomorrow_focus: Optional[str] = None

class DailySummaryRead(BaseModel):
    id: int
    entry_date: date
    highlight: Optional[str] = None
    challenge: Optional[str] = None
    energy_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    gratitude: Optional[str] = None
    tomorrow_focus: Optional[str] = None
    created_datetime: datetime

    class Config:
        from_attributes = True

# --- Daily Summary Endpoints ---
@router.post("/", response_model=DailySummaryRead, status_code=status.HTTP_201_CREATED)
def create_or_update_daily_summary(*, summary: DailySummaryCreate, db: Session = Depends(get_db)):
    # Check if a summary for this date already exists
    db_summary = db.query(DailySummary).filter(DailySummary.entry_date == summary.date).first()
    
    if db_summary:
        # If exists, update it
        summary_data = summary.model_dump(exclude_unset=True)
        # Manually map 'date' from input to 'entry_date' for existing object
        if 'date' in summary_data:
            summary_data['entry_date'] = summary_data.pop('date')
        for key, value in summary_data.items():
            setattr(db_summary, key, value)
        db_summary.created_datetime = datetime.utcnow() # Update timestamp on change
    else:
        # If not, create new
        db_summary = DailySummary(entry_date=summary.date, **summary.model_dump(exclude_unset=True, exclude={'date'}))
    
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

@router.get("/", response_model=List[DailySummaryRead])
def get_daily_summaries(*, db: Session = Depends(get_db), from_date: Optional[date] = None, to_date: Optional[date] = None):
    query = db.query(DailySummary)
    if from_date:
        query = query.filter(DailySummary.entry_date >= from_date)
    if to_date:
        query = query.filter(DailySummary.entry_date <= to_date)
    summaries = query.all()
    return summaries

@router.get("/{summary_date}", response_model=DailySummaryRead)
def get_daily_summary(*, db: Session = Depends(get_db), summary_date: date):
    summary = db.query(DailySummary).filter(DailySummary.entry_date == summary_date).first()
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DailySummary not found for this date")
    return summary

@router.patch("/{summary_date}", response_model=DailySummaryRead)
def update_daily_summary(*, db: Session = Depends(get_db), summary_date: date, summary: DailySummaryUpdate):
    db_summary = db.query(DailySummary).filter(DailySummary.entry_date == summary_date).first()
    if not db_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DailySummary not found for this date")
    
    summary_data = summary.model_dump(exclude_unset=True)
    for key, value in summary_data.items():
        setattr(db_summary, key, value)
    
    db_summary.created_datetime = datetime.utcnow() # Update timestamp on change
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

@router.delete("/{summary_date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_daily_summary(*, db: Session = Depends(get_db), summary_date: date):
    db_summary = db.query(DailySummary).filter(DailySummary.entry_date == summary_date).first()
    if not db_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DailySummary not found for this date")
    
    db.delete(db_summary)
    db.commit()
    return {"ok": True}