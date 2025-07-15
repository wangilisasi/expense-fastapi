# JWT + OAuth2 Authentication Implementation Guide

This document outlines the step-by-step process of implementing JWT-based authentication with OAuth2 in our FastAPI expense tracker application.

## Overview

We implemented a complete authentication system that includes:
- User registration and login
- JWT token-based authentication
- Password hashing with bcrypt
- User-specific data access
- Protected API endpoints

## Step 1: Add Authentication Dependencies

**File:** `requirements.txt`

Added the following packages:
```
python-jose[cryptography]==3.3.0  # JWT token handling
passlib[bcrypt]==1.7.4           # Password hashing
```

**Purpose:** These libraries provide the core functionality for JWT tokens and secure password hashing.

## Step 2: Create User Model

**File:** `app/models.py`

Added the `User` model:
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    expense_trackers = relationship("ExpenseTracker", back_populates="user")
```

**Purpose:** Store user credentials and establish relationships with expense trackers.

## Step 3: Update ExpenseTracker Model

**File:** `app/models.py`

Modified the `ExpenseTracker` model to link to users:
```python
class ExpenseTracker(Base):
    # ... existing fields ...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ... existing relationships ...
    user = relationship("User", back_populates="expense_trackers")
```

**Purpose:** Establish ownership relationship between users and their expense trackers.

## Step 4: Create Authentication Schemas

**File:** `app/schemas.py`

Added authentication-related schemas:
```python
# Input schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Response schemas
class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
```

**Purpose:** Define data structures for API requests and responses related to authentication.

## Step 5: Create Authentication Utilities

**File:** `app/auth.py`

Implemented core authentication functions:

### Configuration
```python
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Password Handling
```python
def verify_password(plain_password: str, hashed_password: str) -> bool
def get_password_hash(password: str) -> str
```

### User Management
```python
def get_user_by_username(db: Session, username: str) -> Optional[models.User]
def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]
```

### JWT Token Management
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User
async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User
```

**Purpose:** Centralize all authentication logic including password hashing, token creation, and user validation.

## Step 6: Add Authentication Endpoints

**File:** `main.py`

Added three new endpoints:

### User Registration
```python
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check for existing username/email
    # Hash password
    # Create user in database
```

### User Login
```python
@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user
    # Create JWT token
    # Return token
```

### Get Current User
```python
@app.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_active_user)):
    # Return current user info
```

**Purpose:** Provide API endpoints for user registration, login, and profile access.

## Step 7: Protect Existing Endpoints

**File:** `main.py`

Updated all existing endpoints to require authentication:

### Before (Unprotected)
```python
@app.get("/trackers", response_model=List[schemas.ExpenseTracker])
def get_trackers(db: Session = Depends(get_db)):
    trackers = db.query(models.ExpenseTracker).all()
    return trackers
```

### After (Protected & User-Specific)
```python
@app.get("/trackers", response_model=List[schemas.ExpenseTracker])
def get_trackers(current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    trackers = db.query(models.ExpenseTracker).filter(models.ExpenseTracker.user_id == current_user.id).all()
    return trackers
```

**Applied to all endpoints:**
- `/trackers` (GET, POST)
- `/trackers/{id}` (GET)
- `/trackers/{trackerId}/expenses` (GET)
- `/expenses` (POST)
- `/expenses/{id}` (DELETE)

**Purpose:** Ensure all data access is user-specific and requires authentication.

## Authentication Flow

### 1. User Registration
```
POST /register
Body: {"username": "john", "email": "john@example.com", "password": "secret123"}
Response: {"id": 1, "username": "john", "email": "john@example.com"}
```

### 2. User Login
```
POST /login
Body: {"username": "john", "password": "secret123"}
Response: {"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", "token_type": "bearer"}
```

### 3. Access Protected Endpoints
```
GET /trackers
Headers: {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
Response: [user's trackers]
```

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with 30-minute expiration
- **User Isolation**: Each user can only access their own data
- **Input Validation**: Pydantic schemas validate all inputs
- **Error Handling**: Proper HTTP status codes and error messages

## Key Benefits

1. **Scalable**: JWT tokens are stateless and don't require server-side storage
2. **Secure**: Industry-standard bcrypt hashing and JWT implementation
3. **User-Friendly**: Clear registration and login flow
4. **Maintainable**: Clean separation of concerns between auth logic and business logic
5. **FastAPI Native**: Uses FastAPI's built-in security utilities

## Production Considerations

- [ ] Change `SECRET_KEY` in `app/auth.py` to a secure random string
- [ ] Consider adding email verification for registration
- [ ] Implement password reset functionality
- [ ] Add refresh token mechanism for longer sessions
- [ ] Consider rate limiting for auth endpoints
- [ ] Add logging for security events

## Testing the Implementation

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start the server**: `uvicorn main:app --reload`
3. **Register a user**: POST to `/register`
4. **Login**: POST to `/login` to get token
5. **Access protected endpoints**: Include `Authorization: Bearer <token>` header

The authentication system is now fully functional and integrated with the existing expense tracker application. 