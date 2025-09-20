from fastapi import FastAPI, HTTPException, Response, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta, date
from sqlalchemy.orm import Session, selectinload

from app.database import engine, get_db
import app.models as models
import app.schemas as schemas
import app.auth as auth

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# --- Auth Endpoints ---

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = auth.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user


# --- ExpenseTracker Endpoints ---

@app.get("/trackers", response_model=List[schemas.ExpenseTracker])
def get_trackers(current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    try:
        # Query trackers for the current user using UUID
        trackers = db.query(models.ExpenseTracker).filter(
            models.ExpenseTracker.uuid_user_id == current_user.uuid_id
        ).all()
        
        # Return trackers (empty list if none found)
        return trackers
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving trackers. Please try again later."
        )

@app.post("/trackers", response_model=schemas.ExpenseTracker)
def create_tracker(tracker: schemas.ExpenseTrackerCreate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    db_tracker = models.ExpenseTracker(**tracker.model_dump(), uuid_user_id=current_user.uuid_id, user_id=current_user.id)
    db.add(db_tracker)
    db.commit()
    db.refresh(db_tracker)
    return db_tracker

@app.get("/trackers/{uuid_id}", response_model=schemas.ExpenseTrackerWithExpenses)
def get_tracker_details(uuid_id: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    # First check if tracker exists at all
    tracker = (
        db.query(models.ExpenseTracker)
        .filter(models.ExpenseTracker.uuid_id == uuid_id)
        .options(selectinload(models.ExpenseTracker.expenses))
        .first()
    )
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Then verify the tracker belongs to the current user
    if tracker.uuid_user_id != current_user.uuid_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this tracker")
    
    return tracker

@app.patch("/trackers/{uuid_id}", response_model=schemas.ExpenseTracker)
def update_tracker(uuid_id: str, tracker_update: schemas.ExpenseTrackerUpdate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Update an expense tracker (PATCH - only specified fields)"""
    # Get the existing tracker
    db_tracker = db.query(models.ExpenseTracker).filter(
        models.ExpenseTracker.uuid_id == uuid_id,
        models.ExpenseTracker.uuid_user_id == current_user.uuid_id
    ).first()
    
    if not db_tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Update only the provided fields
    update_data = tracker_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tracker, field, value)
    
    db.commit()
    db.refresh(db_tracker)
    return db_tracker

@app.get("/trackers/{uuid_id}/stats", response_model=schemas.ExpenseTrackerStats)
def get_tracker_stats(uuid_id: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    # First check if tracker exists and belongs to the current user
    tracker = (
        db.query(models.ExpenseTracker)
        .filter(models.ExpenseTracker.uuid_id == uuid_id)
        .options(selectinload(models.ExpenseTracker.expenses))
        .first()
    )
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Verify the tracker belongs to the current user
    if tracker.uuid_user_id != current_user.uuid_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this tracker")
    
    # Calculate stats
    today = date.today()
    
    # Calculate remaining days (0 if end date has passed)
    remaining_days = max(0, (tracker.endDate - today).days)+1

     # Today's expenditure
    todays_expenditure = round(
        sum(expense.amount for expense in tracker.expenses if expense.date == today),
        2,
    )
    
    # Calculate total period in days
    #total_period_days = (tracker.endDate - tracker.startDate).days + 1  # +1 to include both start and end dates
       
    # Calculate total expenditure by summing all expenses (rounded to 2 decimal places)
    total_expenditure = round(sum(expense.amount for expense in tracker.expenses), 2)
    
    # Calculate average expenditure per day so far (from startDate to today or endDate, whichever is earlier)
    period_end_for_avg = min(today, tracker.endDate)
    if period_end_for_avg < tracker.startDate:
        elapsed_days = 0
    else:
        elapsed_days = (period_end_for_avg - tracker.startDate).days + 1
    average_expenditure_per_day = round(total_expenditure / elapsed_days, 2) if elapsed_days > 0 else 0

    # Calculate target expenditure per day (rounded to 2 decimal places)
    target_expenditure_per_day = round((tracker.budget-total_expenditure) / remaining_days if remaining_days > 0 else 0, 2)

    
    return schemas.ExpenseTrackerStats(
        start_date=tracker.startDate,
        end_date=tracker.endDate,
        budget=round(tracker.budget, 2),
        remaining_days=remaining_days,
        target_expenditure_per_day=target_expenditure_per_day,
        average_expenditure_per_day=average_expenditure_per_day,
        total_expenditure=total_expenditure,
        todays_expenditure=todays_expenditure,
    )

# --- Expense Endpoints ---

@app.get("/trackers/{tracker_uuid_id}/expenses", response_model=List[schemas.Expense])
def get_expenses_for_tracker(tracker_uuid_id: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    # First check if tracker exists at all
    tracker = db.query(models.ExpenseTracker).filter(models.ExpenseTracker.uuid_id == tracker_uuid_id).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Then verify the tracker belongs to the current user
    if tracker.uuid_user_id != current_user.uuid_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this tracker")
    
    expenses = (db.query(models.Expense)
    .filter(models.Expense.uuid_tracker_id == tracker_uuid_id)
    .order_by(models.Expense.uuid_id.desc())
    .limit(5)
    .all()
    )
    return expenses

@app.post("/expenses", response_model=schemas.Expense, status_code=status.HTTP_201_CREATED)
def add_expense(expense_in: schemas.ExpenseCreate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    # First check if tracker exists at all
    tracker = db.query(models.ExpenseTracker).filter(
        models.ExpenseTracker.uuid_id == expense_in.uuid_tracker_id
    ).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Then verify the tracker belongs to the current user
    if tracker.uuid_user_id != current_user.uuid_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add expenses to this tracker")

    # Create expense with both UUID and old integer foreign keys for compatibility
    expense_data = expense_in.model_dump()
    expense_data['trackerId'] = tracker.id  # Set the old integer foreign key for compatibility
    db_expense = models.Expense(**expense_data)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.delete("/expenses/{uuid_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(uuid_id: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.uuid_id == uuid_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Verify the expense belongs to a tracker owned by the current user
    tracker = db.query(models.ExpenseTracker).filter(
        models.ExpenseTracker.uuid_id == expense.uuid_tracker_id,
        models.ExpenseTracker.uuid_user_id == current_user.uuid_id
    ).first()
    if not tracker:
        # The expense exists but the current user does not own the associated tracker
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this expense")
    
    db.delete(expense)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/trackers/{tracker_uuid_id}/daily-expenses", response_model=schemas.DailyExpensesResponse)
def get_daily_expenses(tracker_uuid_id: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Get daily expense totals grouped by date for a specific tracker"""
    # First check if tracker exists and belongs to the current user
    tracker = db.query(models.ExpenseTracker).filter(
        models.ExpenseTracker.uuid_id == tracker_uuid_id,
        models.ExpenseTracker.uuid_user_id == current_user.uuid_id
    ).first()
    
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Get all expenses for this tracker, ordered by date descending
    expenses = (
        db.query(models.Expense)
        .filter(models.Expense.uuid_tracker_id == tracker_uuid_id)
        .order_by(models.Expense.date.desc(), models.Expense.uuid_id.desc())
        .all()
    )
    
    # Group expenses by date
    daily_expenses_dict = {}
    for expense in expenses:
        expense_date = expense.date
        
        if expense_date not in daily_expenses_dict:
            daily_expenses_dict[expense_date] = {
                "date": expense_date,
                "total_amount": 0,
                "transactions": []
            }
        
        # Add expense to the day's transactions
        daily_expenses_dict[expense_date]["transactions"].append({
            "uuid_id": expense.uuid_id,
            "id": expense.id,  # Keep for backward compatibility
            "name": expense.description,
            "amount": expense.amount
        })
        
        # Add to daily total
        daily_expenses_dict[expense_date]["total_amount"] += expense.amount
    
    # Convert to list and sort by date (most recent first)
    daily_expenses_list = list(daily_expenses_dict.values())
    daily_expenses_list.sort(key=lambda x: x["date"], reverse=True)
    
    # Limit to 5 most recent days
    daily_expenses_list = daily_expenses_list[:5]
    
    # Round the total amounts to 2 decimal places
    for day in daily_expenses_list:
        day["total_amount"] = round(day["total_amount"], 2)
    
    return schemas.DailyExpensesResponse(daily_expenses=daily_expenses_list)