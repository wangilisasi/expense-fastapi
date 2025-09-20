from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date
import uuid

# --- Auth Schemas ---

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    uuid_id: str
    # Keep old id for backward compatibility during migration
    id: Optional[int] = None
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Base Schemas ---

class ExpenseBase(BaseModel):
    description: str
    amount: float
    date: date

# --- Create Schemas ---
class ExpenseCreate(ExpenseBase):
    uuid_tracker_id: str
    # Keep old trackerId for backward compatibility during migration
    trackerId: Optional[int] = None

# --- Update Schemas ---
class ExpenseTrackerUpdate(BaseModel):
    """Schema for updating an expense tracker (PATCH - partial updates)"""
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    budget: Optional[float] = None
    name: Optional[str] = None
    description: Optional[str] = None

class Expense(ExpenseBase):
    uuid_id: str
    uuid_tracker_id: str
    # Keep old fields for backward compatibility during migration
    id: Optional[int] = None
    trackerId: Optional[int] = None
    class Config:
        from_attributes = True

class ExpenseTrackerBase(BaseModel):
    startDate: date
    endDate: date
    budget: float
    name: str
    description: Optional[str] = None

class ExpenseTrackerCreate(ExpenseTrackerBase):
    pass

class ExpenseTracker(ExpenseTrackerBase):
    uuid_id: str
    expenses: List[Expense] = []
    # Keep old id for backward compatibility during migration
    id: Optional[int] = None
    class Config:
        from_attributes = True


# --- Schemas with Relationships ---

class ExpenseTrackerWithExpenses(ExpenseTracker):
    expenses: List[Expense] = []

# --- Stats Schema ---

class ExpenseTrackerStats(BaseModel):
    start_date: date
    end_date: date
    budget: float
    remaining_days: int
    target_expenditure_per_day: float
    average_expenditure_per_day: float
    total_expenditure: float
    todays_expenditure: float
    class Config:
        from_attributes = True

# --- Daily Expense Schemas ---

class DailyExpenseTransaction(BaseModel):
    uuid_id: str
    name: str
    amount: float
    # Keep old id for backward compatibility during migration
    id: Optional[int] = None
    
    class Config:
        from_attributes = True

class DailyExpenseGroup(BaseModel):
    date: date
    total_amount: float
    transactions: List[DailyExpenseTransaction]

class DailyExpensesResponse(BaseModel):
    daily_expenses: List[DailyExpenseGroup]

