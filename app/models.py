from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class ExpenseTracker(Base):
    __tablename__ = "expensetracker"

    id = Column(Integer, primary_key=True)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    budget = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    expenses = relationship("Expense", back_populates="tracker")

class Expense(Base):
    __tablename__ = "expense"

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    trackerId = Column(Integer, ForeignKey("expensetracker.id"))

    tracker = relationship("ExpenseTracker", back_populates="expenses") 