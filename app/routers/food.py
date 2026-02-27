from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel # For API Request/Response Models

from ..database import get_db # Use get_db for SQLAlchemy sessions
from ..models import FoodLog # SQLAlchemy ORM models
from ..auth import get_api_key

from sqlalchemy.orm import Session # Import Session from SQLAlchemy

router = APIRouter(prefix="/food", tags=["food"], dependencies=[Depends(get_api_key)])

# Pydantic models for request bodies
class FoodLogCreate(BaseModel):
    description: str
    meal_type: Optional[str] = None
    notes: Optional[str] = None

class FoodLogUpdate(BaseModel):
    description: Optional[str] = None
    meal_type: Optional[str] = None
    notes: Optional[str] = None

class FoodLogRead(BaseModel):
    id: int
    description: str
    meal_type: Optional[str] = None
    logged_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# --- Food Log Endpoints ---
@router.post("/", response_model=FoodLogRead, status_code=status.HTTP_201_CREATED)
def create_food_log(*, food_log: FoodLogCreate, db: Session = Depends(get_db)):
    db_food_log = FoodLog(**food_log.model_dump())
    db.add(db_food_log)
    db.commit()
    db.refresh(db_food_log)
    return db_food_log

@router.get("/", response_model=List[FoodLogRead])
def get_food_logs(*, db: Session = Depends(get_db), date: Optional[date] = None):
    query = db.query(FoodLog)
    if date:
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        query = query.filter(FoodLog.logged_at >= start_of_day).filter(FoodLog.logged_at <= end_of_day)
    food_logs = query.all()
    return food_logs

@router.get("/{food_log_id}", response_model=FoodLogRead)
def get_food_log(*, db: Session = Depends(get_db), food_log_id: int):
    food_log = db.query(FoodLog).filter(FoodLog.id == food_log_id).first()
    if not food_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodLog not found")
    return food_log

@router.patch("/{food_log_id}", response_model=FoodLogRead)
def update_food_log(*, db: Session = Depends(get_db), food_log_id: int, food_log: FoodLogUpdate):
    db_food_log = db.query(FoodLog).filter(FoodLog.id == food_log_id).first()
    if not db_food_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodLog not found")
    
    food_log_data = food_log.model_dump(exclude_unset=True)
    for key, value in food_log_data.items():
        setattr(db_food_log, key, value)
    
    db.add(db_food_log)
    db.commit()
    db.refresh(db_food_log)
    return db_food_log

@router.delete("/{food_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_log(*, db: Session = Depends(get_db), food_log_id: int):
    food_log = db.query(FoodLog).filter(FoodLog.id == food_log_id).first()
    if not food_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FoodLog not found")
    db.delete(food_log)
    db.commit()
    return {"ok": True}