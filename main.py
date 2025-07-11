from fastapi import FastAPI, HTTPException, Response, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_session, init_db
from datetime import date

# --- SQLModel Models ---

class ExpenseTrackerBase(SQLModel):
    startDate: date
    endDate: date
    budget: float
    name: str
    description: Optional[str] = None

class ExpenseTracker(ExpenseTrackerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    expenses: List["Expense"] = Relationship(back_populates="tracker")

class ExpenseTrackerCreate(ExpenseTrackerBase):
    pass

class ExpenseTrackerRead(ExpenseTrackerBase):
    id: int

class ExpenseBase(SQLModel):
    description: str
    amount: float
    date: date
    trackerId: Optional[int] = Field(default=None, foreign_key="expensetracker.id")

class Expense(ExpenseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracker: Optional[ExpenseTracker] = Relationship(back_populates="expenses")

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseRead(ExpenseBase):
    id: int

class ExpenseReadWithTracker(ExpenseRead):
    tracker: Optional[ExpenseTrackerRead] = None

class ExpenseTrackerReadWithExpenses(ExpenseTrackerRead):
    expenses: List[ExpenseRead] = []


# --- FastAPI App ---
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

# --- ExpenseTracker Endpoints ---

@app.get("/trackers", response_model=List[ExpenseTrackerRead])
async def get_trackers(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ExpenseTracker))
    trackers = result.scalars().all()
    return trackers

@app.post("/trackers", response_model=ExpenseTrackerRead)
async def create_tracker(tracker: ExpenseTrackerCreate, session: AsyncSession = Depends(get_session)):
    db_tracker = ExpenseTracker.from_orm(tracker)
    session.add(db_tracker)
    await session.commit()
    await session.refresh(db_tracker)
    return db_tracker

@app.get("/trackers/{id}", response_model=ExpenseTrackerReadWithExpenses)
async def get_tracker_details(id: int, session: AsyncSession = Depends(get_session)):
    tracker = await session.get(ExpenseTracker, id, options=[select(Expense)])
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    return tracker

# --- Expense Endpoints ---

@app.get("/trackers/{trackerId}/expenses", response_model=List[ExpenseRead])
async def get_expenses_for_tracker(trackerId: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Expense).where(Expense.trackerId == trackerId))
    expenses = result.scalars().all()
    return expenses

@app.post("/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def add_expense(expense_in: ExpenseCreate, session: AsyncSession = Depends(get_session)):
    # Verify tracker exists
    tracker = await session.get(ExpenseTracker, expense_in.trackerId)
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found for this expense")

    db_expense = Expense.from_orm(expense_in)
    session.add(db_expense)
    await session.commit()
    await session.refresh(db_expense)
    return db_expense

@app.delete("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(id: int, session: AsyncSession = Depends(get_session)):
    expense = await session.get(Expense, id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    await session.delete(expense)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)