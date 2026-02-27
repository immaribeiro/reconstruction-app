from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel # For API Request/Response Models

from ..database import get_db # Use get_db for SQLAlchemy sessions
from ..models import Reminder, ReminderStatus # SQLAlchemy ORM models
from ..auth import get_api_key

from sqlalchemy.orm import Session # Import Session from SQLAlchemy

router = APIRouter(prefix="/reminders", tags=["reminders"], dependencies=[Depends(get_api_key)])

# Pydantic models for request bodies
class ReminderCreate(BaseModel):
    text: str
    due_at: Optional[datetime] = None

class ReminderUpdate(BaseModel):
    text: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[ReminderStatus] = None

class ReminderRead(BaseModel):
    id: int
    text: str
    due_at: Optional[datetime] = None
    status: ReminderStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Reminder Endpoints ---
@router.post("/", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(*, reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = Reminder(**reminder.model_dump())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@router.get("/", response_model=List[ReminderRead])
def get_reminders(*, db: Session = Depends(get_db), status: Optional[ReminderStatus] = None):
    query = db.query(Reminder)
    if status:
        query = query.filter(Reminder.status == status)
    reminders = query.all()
    return reminders

@router.get("/{reminder_id}", response_model=ReminderRead)
def get_reminder(*, db: Session = Depends(get_db), reminder_id: int):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return reminder

@router.patch("/{reminder_id}", response_model=ReminderRead)
def update_reminder(*, db: Session = Depends(get_db), reminder_id: int, reminder: ReminderUpdate):
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not db_reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    
    reminder_data = reminder.model_dump(exclude_unset=True)
    for key, value in reminder_data.items():
        setattr(db_reminder, key, value)
    
    # Handle status change to DONE
    if "status" in reminder_data and reminder_data["status"] == ReminderStatus.DONE:
        db_reminder.completed_at = datetime.utcnow()
    elif "status" in reminder_data and reminder_data["status"] != ReminderStatus.DONE:
        db_reminder.completed_at = None

    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(*, db: Session = Depends(get_db), reminder_id: int):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"ok": True}