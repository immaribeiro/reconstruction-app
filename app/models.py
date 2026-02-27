from datetime import datetime, date
from typing import List, Optional
from enum import Enum

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped
from sqlalchemy.sql import func # For default timestamps

Base = declarative_base()

# --- Enum for Reminder Status ---
class ReminderStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    DISMISSED = "disposed"

# --- Main Models ---
class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    text: Mapped[str] = Column(String, nullable=False)
    due_at: Mapped[Optional[datetime]] = Column(DateTime)
    status: Mapped[ReminderStatus] = Column(String, default=ReminderStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = Column(DateTime)

class FoodLog(Base):
    __tablename__ = "foodlogs"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    description: Mapped[str] = Column(String, nullable=False)
    meal_type: Mapped[Optional[str]] = Column(String)
    logged_at: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)
    notes: Mapped[Optional[str]] = Column(String)

class TrainingLog(Base):
    __tablename__ = "traininglogs"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    activity: Mapped[str] = Column(String, nullable=False)
    duration_minutes: Mapped[Optional[int]] = Column(Integer)
    intensity: Mapped[Optional[str]] = Column(String)
    logged_at: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)
    notes: Mapped[Optional[str]] = Column(String)

class MentalLog(Base):
    __tablename__ = "mentallogs"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    content: Mapped[str] = Column(String, nullable=False)
    mood: Mapped[Optional[str]] = Column(String)
    tags: Mapped[Optional[str]] = Column(String)
    logged_at: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)

class DailySummary(Base):
    __tablename__ = "dailysummaries"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    entry_date: Mapped[date] = Column(Date, unique=True, index=True, nullable=False)
    highlight: Mapped[Optional[str]] = Column(String)
    challenge: Mapped[Optional[str]] = Column(String)
    energy_level: Mapped[Optional[int]] = Column(Integer)
    sleep_quality: Mapped[Optional[int]] = Column(Integer)
    gratitude: Mapped[Optional[str]] = Column(String)
    tomorrow_focus: Mapped[Optional[str]] = Column(String)
    created_datetime: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)

class CostCategory(Base):
    __tablename__ = "costcategories"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = Column(String)

    articles: Mapped[List["CostArticle"]] = relationship(back_populates="category")

class CostArticle(Base):
    __tablename__ = "costarticles"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = Column(Integer, ForeignKey("costcategories.id"), nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    total_budgeted_amount: Mapped[Optional[float]] = Column(Float)

    category: Mapped["CostCategory"] = relationship(back_populates="articles")
    transactions: Mapped[List["CostTransaction"]] = relationship(back_populates="article")

class CostTransaction(Base):
    __tablename__ = "costtransactions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    article_id: Mapped[int] = Column(Integer, ForeignKey("costarticles.id"), nullable=False)
    transaction_date: Mapped[date] = Column(Date, nullable=False)
    phase_number: Mapped[Optional[int]] = Column(Integer)
    payment_method: Mapped[str] = Column(String, nullable=False)
    amount: Mapped[float] = Column(Float, nullable=False)
    has_invoice: Mapped[bool] = Column(Boolean, nullable=False)
    notes: Mapped[Optional[str]] = Column(String)
    created_datetime: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)

    article: Mapped["CostArticle"] = relationship(back_populates="transactions")