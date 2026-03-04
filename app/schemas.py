from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime
from enum import Enum
import uuid

# --- Category Enum ---

class CategoryEnum(str, Enum):
    food = "Food"
    transport = "Transport"
    housing = "Housing"
    entertainment = "Entertainment"
    health = "Health"
    shopping = "Shopping"
    utilities = "Utilities"
    education = "Education"
    other = "Other"

# --- Auth Schemas ---

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    uuid_id: str
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
    category: CategoryEnum = CategoryEnum.other

# --- Create Schemas ---
class ExpenseCreate(ExpenseBase):
    uuid_id: str  # Client-generated stable UUID for idempotent creation
    uuid_tracker_id: str

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
    category: CategoryEnum = CategoryEnum.other
    created_at: datetime
    updated_at: datetime
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

class ExpenseTrackerSummary(ExpenseTrackerBase):
    """Lightweight tracker schema — no expenses embedded.
    
    Used by GET /trackers (list) so the response stays small regardless
    of how many expenses each tracker has accumulated.
    """
    uuid_id: str
    class Config:
        from_attributes = True

class ExpenseTracker(ExpenseTrackerBase):
    uuid_id: str
    expenses: List[Expense] = []
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
    category: CategoryEnum = CategoryEnum.other

    class Config:
        from_attributes = True

class DailyExpenseGroup(BaseModel):
    date: date
    total_amount: float
    transactions: List[DailyExpenseTransaction]

class DailyExpensesResponse(BaseModel):
    daily_expenses: List[DailyExpenseGroup]


# --- Category Analytics Schemas ---

class CategoryBreakdown(BaseModel):
    category: CategoryEnum
    total_amount: float
    percentage: float        # % of total expenditure
    expense_count: int

class CategoryAnalyticsResponse(BaseModel):
    tracker_uuid_id: str
    total_expenditure: float
    categories: List[CategoryBreakdown]

