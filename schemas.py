from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

# --- Base Schemas ---

class ExpenseBase(BaseModel):
    description: str
    amount: float
    date: date

# --- Create Schemas ---
class ExpenseCreate(ExpenseBase):
    trackerId: int

class Expense(ExpenseBase):
    id: int
    trackerId: int
    class Config:
        orm_mode = True

class ExpenseTrackerBase(BaseModel):
    startDate: date
    endDate: date
    budget: float
    name: str
    description: Optional[str] = None

class ExpenseTrackerCreate(ExpenseTrackerBase):
    pass

class ExpenseTracker(ExpenseTrackerBase):
    id: int
    expenses: List[Expense] = []
    class Config:
        orm_mode = True


# --- Schemas with Relationships ---

class ExpenseTrackerWithExpenses(ExpenseTracker):
    expenses: List[Expense] = []

