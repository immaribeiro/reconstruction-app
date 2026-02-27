from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel # For API Request/Response Models

from ..database import get_db # Use get_db for SQLAlchemy sessions
from ..models import TrainingLog # SQLAlchemy ORM models
from ..auth import get_api_key

from sqlalchemy.orm import Session # Import Session from SQLAlchemy

router = APIRouter(prefix="/training", tags=["training"], dependencies=[Depends(get_api_key)])

# Pydantic models for request bodies
class TrainingLogCreate(BaseModel):
    activity: str
    duration_minutes: Optional[int] = None
    intensity: Optional[str] = None
    notes: Optional[str] = None

class TrainingLogUpdate(BaseModel):
    activity: Optional[str] = None
    duration_minutes: Optional[int] = None
    intensity: Optional[str] = None
    notes: Optional[str] = None

class TrainingLogRead(BaseModel):
    id: int
    activity: str
    duration_minutes: Optional[int] = None
    intensity: Optional[str] = None
    logged_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# --- Training Log Endpoints ---
@router.post("/", response_model=TrainingLogRead, status_code=status.HTTP_201_CREATED)
def create_training_log(*, training_log: TrainingLogCreate, db: Session = Depends(get_db)):
    db_training_log = TrainingLog(**training_log.model_dump())
    db.add(db_training_log)
    db.commit()
    db.refresh(db_training_log)
    return db_training_log

@router.get("/", response_model=List[TrainingLogRead])
def get_training_logs(*, db: Session = Depends(get_db), date: Optional[date] = None):
    query = db.query(TrainingLog)
    if date:
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        query = query.filter(TrainingLog.logged_at >= start_of_day).filter(TrainingLog.logged_at <= end_of_day)
    training_logs = query.all()
    return training_logs

@router.get("/{training_log_id}", response_model=TrainingLogRead)
def get_training_log(*, db: Session = Depends(get_db), training_log_id: int):
    training_log = db.query(TrainingLog).filter(TrainingLog.id == training_log_id).first()
    if not training_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TrainingLog not found")
    return training_log

@router.patch("/{training_log_id}", response_model=TrainingLogRead)
def update_training_log(*, db: Session = Depends(get_db), training_log_id: int, training_log: TrainingLogUpdate):
    db_training_log = db.query(TrainingLog).filter(TrainingLog.id == training_log_id).first()
    if not db_training_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TrainingLog not found")
    
    training_log_data = training_log.model_dump(exclude_unset=True)
    for key, value in training_log_data.items():
        setattr(db_training_log, key, value)
    
    db.add(db_training_log)
    db.commit()
    db.refresh(db_training_log)
    return db_training_log

@router.delete("/{training_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_log(*, db: Session = Depends(get_db), training_log_id: int):
    training_log = db.query(TrainingLog).filter(TrainingLog.id == training_log_id).first()
    if not training_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TrainingLog not found")
    db.delete(training_log)
    db.commit()
    return {"ok": True}