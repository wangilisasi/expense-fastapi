from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # UUID primary key
    uuid_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    expense_trackers = relationship("ExpenseTracker", back_populates="user", foreign_keys="ExpenseTracker.uuid_user_id")

class ExpenseTracker(Base):
    __tablename__ = "expensetracker"

    # UUID primary key
    uuid_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    budget = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    # UUID foreign key
    uuid_user_id = Column(String(36), ForeignKey("users.uuid_id"), nullable=False)

    expenses = relationship("Expense", back_populates="tracker", foreign_keys="Expense.uuid_tracker_id")
    user = relationship("User", back_populates="expense_trackers", foreign_keys=[uuid_user_id])

class Expense(Base):
    __tablename__ = "expense"

    # UUID primary key
    uuid_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    # UUID foreign key
    uuid_tracker_id = Column(String(36), ForeignKey("expensetracker.uuid_id"), nullable=False)

    tracker = relationship("ExpenseTracker", back_populates="expenses", foreign_keys=[uuid_tracker_id]) 