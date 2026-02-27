from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Reminder, ReminderStatus
from ..auth import get_api_key

router = APIRouter(prefix="/reminders", tags=["reminders"], dependencies=[Depends(get_api_key)])


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


@router.post("/", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(data: ReminderCreate, db: Session = Depends(get_db)):
    r = Reminder(**data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get("/", response_model=List[ReminderRead])
def list_reminders(db: Session = Depends(get_db), status: Optional[ReminderStatus] = None):
    q = db.query(Reminder)
    if status:
        q = q.filter(Reminder.status == status)
    return q.all()

@router.patch("/{reminder_id}", response_model=ReminderRead)
def update_reminder(reminder_id: int, data: ReminderUpdate, db: Session = Depends(get_db)):
    r = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    update = data.model_dump(exclude_unset=True)
    for k, v in update.items():
        setattr(r, k, v)
    if "status" in update and update["status"] == ReminderStatus.DONE:
        r.completed_at = datetime.utcnow()
    elif "status" in update and update["status"] != ReminderStatus.DONE:
        r.completed_at = None
    db.commit()
    db.refresh(r)
    return r

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    r = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(r)
    db.commit()
