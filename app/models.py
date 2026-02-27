from datetime import datetime, date
from typing import List, Optional
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, Mapped
from sqlalchemy.sql import func

Base = declarative_base()


class ReminderStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    DISMISSED = "dismissed"


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    text: Mapped[str] = Column(String, nullable=False)
    due_at: Mapped[Optional[datetime]] = Column(DateTime)
    status: Mapped[ReminderStatus] = Column(String, default=ReminderStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = Column(DateTime)


class CostCategory(Base):
    """Top-level grouping: Arquiteto, Empreiteiro, Electricista, etc."""
    __tablename__ = "cost_categories"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    budgeted_total: Mapped[Optional[float]] = Column(Float)

    articles: Mapped[List["CostArticle"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class CostArticle(Base):
    """Line items under a category: Projeto arquitetura, Baixada, Giratória, etc."""
    __tablename__ = "cost_articles"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = Column(Integer, ForeignKey("cost_categories.id"), nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    budgeted_amount: Mapped[Optional[float]] = Column(Float)
    notes: Mapped[Optional[str]] = Column(Text)

    category: Mapped["CostCategory"] = relationship(back_populates="articles")
    transactions: Mapped[List["CostTransaction"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class CostTransaction(Base):
    """Individual payments / tranches for an article."""
    __tablename__ = "cost_transactions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    article_id: Mapped[int] = Column(Integer, ForeignKey("cost_articles.id"), nullable=False)
    transaction_date: Mapped[date] = Column(Date, nullable=False)
    phase_number: Mapped[Optional[int]] = Column(Integer)
    payment_method: Mapped[str] = Column(String, nullable=False)  # Dinheiro, Transferência, MBWay, Multibanco, Serviços
    amount: Mapped[float] = Column(Float, nullable=False)
    has_invoice: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = Column(Text)
    created_at: Mapped[datetime] = Column(DateTime, default=func.now(), nullable=False)

    article: Mapped["CostArticle"] = relationship(back_populates="transactions")
