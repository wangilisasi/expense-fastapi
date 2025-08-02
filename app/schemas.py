from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

# --- Auth Schemas ---

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
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
    trackerId: int

# --- Update Schemas ---
class ExpenseTrackerUpdate(BaseModel):
    """Schema for updating an expense tracker (PATCH - partial updates)"""
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    budget: Optional[float] = None
    name: Optional[str] = None
    description: Optional[str] = None

class Expense(ExpenseBase):
    id: int
    trackerId: int
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
    id: int
    expenses: List[Expense] = []
    class Config:
        from_attributes = True


# --- Schemas with Relationships ---

class ExpenseTrackerWithExpenses(ExpenseTracker):
    expenses: List[Expense] = []

