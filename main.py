from fastapi import FastAPI, HTTPException, Response, status, Depends
from typing import List
from sqlalchemy.orm import Session, selectinload

from app.database import engine, get_db
import app.models as models
import app.schemas as schemas

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# --- ExpenseTracker Endpoints ---

@app.get("/trackers", response_model=List[schemas.ExpenseTracker])
def get_trackers(db: Session = Depends(get_db)):
    trackers = db.query(models.ExpenseTracker).all()
    return trackers

@app.post("/trackers", response_model=schemas.ExpenseTracker)
def create_tracker(tracker: schemas.ExpenseTrackerCreate, db: Session = Depends(get_db)):
    db_tracker = models.ExpenseTracker(**tracker.model_dump())
    db.add(db_tracker)
    db.commit()
    db.refresh(db_tracker)
    return db_tracker

@app.get("/trackers/{id}", response_model=schemas.ExpenseTrackerWithExpenses)
def get_tracker_details(id: int, db: Session = Depends(get_db)):
    tracker = (
        db.query(models.ExpenseTracker)
        .filter(models.ExpenseTracker.id == id)
        .options(selectinload(models.ExpenseTracker.expenses))
        .first()
    )
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    return tracker

# --- Expense Endpoints ---

@app.get("/trackers/{trackerId}/expenses", response_model=List[schemas.Expense])
def get_expenses_for_tracker(trackerId: int, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter(models.Expense.trackerId == trackerId).all()
    return expenses

@app.post("/expenses", response_model=schemas.Expense, status_code=status.HTTP_201_CREATED)
def add_expense(expense_in: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    # Verify tracker exists
    tracker = db.get(models.ExpenseTracker, expense_in.trackerId)
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found for this expense")

    db_expense = models.Expense(**expense_in.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.delete("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(id: int, db: Session = Depends(get_db)):
    expense = db.get(models.Expense, id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)