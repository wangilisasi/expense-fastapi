from fastapi import FastAPI, HTTPException, Response, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta
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
        # Query trackers for the current user
        trackers = db.query(models.ExpenseTracker).filter(
            models.ExpenseTracker.user_id == current_user.id
        ).all()
        
        # Return trackers (empty list if none found)
        return trackers
        
    except Exception as e:
        # Handle unexpected database or server errors
        #log error
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving trackers. Please try again later."
        )

@app.post("/trackers", response_model=schemas.ExpenseTracker)
def create_tracker(tracker: schemas.ExpenseTrackerCreate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    db_tracker = models.ExpenseTracker(**tracker.model_dump(), user_id=current_user.id)
    db.add(db_tracker)
    db.commit()
    db.refresh(db_tracker)
    return db_tracker

@app.get("/trackers/{id}", response_model=schemas.ExpenseTrackerWithExpenses)
def get_tracker_details(id: int, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    # First check if tracker exists at all
    tracker = (
        db.query(models.ExpenseTracker)
        .filter(models.ExpenseTracker.id == id)
        .options(selectinload(models.ExpenseTracker.expenses))
        .first()
    )
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Then verify the tracker belongs to the current user
    if tracker.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this tracker")
    
    return tracker

# --- Expense Endpoints ---

@app.get("/trackers/{trackerId}/expenses", response_model=List[schemas.Expense])
def get_expenses_for_tracker(trackerId: int, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    # First check if tracker exists at all
    tracker = db.query(models.ExpenseTracker).filter(models.ExpenseTracker.id == trackerId).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Then verify the tracker belongs to the current user
    if tracker.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this tracker")
    
    expenses = db.query(models.Expense).filter(models.Expense.trackerId == trackerId).all()
    return expenses

@app.post("/expenses", response_model=schemas.Expense, status_code=status.HTTP_201_CREATED)
def add_expense(expense_in: schemas.ExpenseCreate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    # First check if tracker exists at all
    tracker = db.query(models.ExpenseTracker).filter(
        models.ExpenseTracker.id == expense_in.trackerId
    ).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    
    # Then verify the tracker belongs to the current user
    if tracker.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add expenses to this tracker")

    db_expense = models.Expense(**expense_in.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.delete("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(id: int, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    expense = db.get(models.Expense, id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Verify the expense belongs to a tracker owned by the current user
    tracker = db.query(models.ExpenseTracker).filter(
        models.ExpenseTracker.id == expense.trackerId,
        models.ExpenseTracker.user_id == current_user.id
    ).first()
    if not tracker:
        # The expense exists but the current user does not own the associated tracker
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this expense")
    
    db.delete(expense)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)