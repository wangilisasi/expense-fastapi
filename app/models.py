from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    expense_trackers = relationship("ExpenseTracker", back_populates="user")

class ExpenseTracker(Base):
    __tablename__ = "expensetracker"

    id = Column(Integer, primary_key=True, autoincrement=True)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    budget = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    expenses = relationship("Expense", back_populates="tracker")
    user = relationship("User", back_populates="expense_trackers")

class Expense(Base):
    __tablename__ = "expense"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    trackerId = Column(Integer, ForeignKey("expensetracker.id"))

    tracker = relationship("ExpenseTracker", back_populates="expenses") 