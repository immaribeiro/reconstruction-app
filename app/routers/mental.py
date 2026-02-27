from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel # For API Request/Response Models

from ..database import get_db # Use get_db for SQLAlchemy sessions
from ..models import MentalLog # SQLAlchemy ORM models
from ..auth import get_api_key

from sqlalchemy.orm import Session # Import Session from SQLAlchemy
from sqlalchemy import select # Import select for building queries

router = APIRouter(prefix="/mental", tags=["mental"], dependencies=[Depends(get_api_key)])

# Pydantic models for request bodies
class MentalLogCreate(BaseModel):
    content: str
    mood: Optional[str] = None
    tags: Optional[str] = None

class MentalLogUpdate(BaseModel):
    content: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[str] = None

class MentalLogRead(BaseModel):
    id: int
    content: str
    mood: Optional[str] = None
    tags: Optional[str] = None
    logged_at: datetime

    class Config:
        from_attributes = True

# --- Mental Log Endpoints ---
@router.post("/", response_model=MentalLogRead, status_code=status.HTTP_201_CREATED)
def create_mental_log(*, mental_log: MentalLogCreate, db: Session = Depends(get_db)):
    db_mental_log = MentalLog(**mental_log.model_dump())
    db.add(db_mental_log)
    db.commit()
    db.refresh(db_mental_log)
    return db_mental_log

@router.get("/", response_model=List[MentalLogRead])
def get_mental_logs(*, db: Session = Depends(get_db), date: Optional[date] = None, tag: Optional[str] = None):
    query = db.query(MentalLog)
    if date:
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        query = query.filter(MentalLog.logged_at >= start_of_day).filter(MentalLog.logged_at <= end_of_day)
    if tag:
        query = query.filter(MentalLog.tags.ilike(f"%{tag}%")) # SQLAlchemy's ilike for case-insensitive LIKE
    mental_logs = query.all()
    return mental_logs

@router.get("/{mental_log_id}", response_model=MentalLogRead)
def get_mental_log(*, db: Session = Depends(get_db), mental_log_id: int):
    mental_log = db.query(MentalLog).filter(MentalLog.id == mental_log_id).first()
    if not mental_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MentalLog not found")
    return mental_log

@router.patch("/{mental_log_id}", response_model=MentalLogRead)
def update_mental_log(*, db: Session = Depends(get_db), mental_log_id: int, mental_log: MentalLogUpdate):
    db_mental_log = db.query(MentalLog).filter(MentalLog.id == mental_log_id).first()
    if not db_mental_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MentalLog not found")
    
    mental_log_data = mental_log.model_dump(exclude_unset=True)
    for key, value in mental_log_data.items():
        setattr(db_mental_log, key, value)
    
    db.add(db_mental_log)
    db.commit()
    db.refresh(db_mental_log)
    return db_mental_log

@router.delete("/{mental_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mental_log(*, db: Session = Depends(get_db), mental_log_id: int):
    mental_log = db.query(MentalLog).filter(MentalLog.id == mental_log_id).first()
    if not mental_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MentalLog not found")
    db.delete(mental_log)
    db.commit()
    return {"ok": True}