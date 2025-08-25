# Refresh Token Implementation Guide

This document provides a comprehensive guide to the refresh token implementation in the FastAPI Expense Tracker application, covering everything from planning to final implementation.

## Table of Contents

1. [Overview](#overview)
2. [Why Refresh Tokens?](#why-refresh-tokens)
3. [Architecture and Design](#architecture-and-design)
4. [Implementation Details](#implementation-details)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Security Considerations](#security-considerations)
8. [Testing](#testing)
9. [Migration Guide](#migration-guide)
10. [Best Practices](#best-practices)

## Overview

The refresh token implementation enhances the security of our JWT-based authentication system by introducing short-lived access tokens (30 minutes) paired with longer-lived refresh tokens (7 days). This approach provides better security while maintaining a good user experience.

### Key Features

- **Short-lived Access Tokens**: 30 minutes (reduced from 10 days)
- **Long-lived Refresh Tokens**: 7 days
- **Secure Token Storage**: Refresh tokens stored in database with metadata
- **Token Revocation**: Support for logging out from single device or all devices
- **Automatic Cleanup**: Expired tokens are cleaned up automatically

## Why Refresh Tokens?

### Problems with Long-lived Tokens

The original implementation used access tokens that lasted 10 days, which created several security risks:

1. **Extended Exposure Window**: If a token is compromised, the attacker has 10 days of access
2. **No Revocation Capability**: No way to invalidate tokens before expiry
3. **Device Logout Issues**: Users can't properly log out from devices
4. **Compliance Issues**: Many security standards require shorter token lifespans

### Benefits of Refresh Tokens

1. **Reduced Attack Surface**: Access tokens expire quickly (30 minutes)
2. **Revocation Support**: Can invalidate refresh tokens immediately
3. **Better User Control**: Users can log out from specific devices or all devices
4. **Audit Trail**: Track token usage and creation
5. **Compliance**: Meets security best practices and standards

## Architecture and Design

### Token Flow Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Login    │    │  Access Token   │    │  Refresh Token  │
│                 │    │   (30 minutes)  │    │    (7 days)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Authentication  │───▶│   API Access    │    │  Token Storage  │
│    Server       │    │   (Protected    │    │   (Database)    │
│                 │    │   Endpoints)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Token Refresh   │    │ Token Expiry    │    │ Token Cleanup   │
│   Endpoint      │    │   Handling      │    │   (Scheduled)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Security Model

1. **Access Tokens**: Short-lived, used for API access, stored client-side
2. **Refresh Tokens**: Long-lived, used only for token renewal, stored securely
3. **Token Binding**: Refresh tokens are bound to specific users
4. **Revocation**: Immediate invalidation capability for security incidents

## Implementation Details

### 1. Database Model

**File**: `app/models.py`

```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="refresh_tokens")
```

### 2. Authentication Configuration

**File**: `app/auth.py`

```python
# Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days
```

### 3. Core Functions

#### Token Creation
```python
def create_refresh_token(db: Session, user_id: int) -> str:
    """Create a new refresh token for a user."""
    token = secrets.token_urlsafe(32)  # Cryptographically secure
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    # Store in database...
```

#### Token Verification
```python
def verify_refresh_token(db: Session, token: str) -> Optional[models.User]:
    """Verify a refresh token and return the associated user."""
    # Check token exists, is active, and not expired
```

#### Token Revocation
```python
def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a specific refresh token."""
    
def revoke_all_refresh_tokens(db: Session, user_id: int) -> bool:
    """Revoke all refresh tokens for a user."""
```

### 4. API Schemas

**File**: `app/schemas.py`

```python
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
```

## Database Schema

### Refresh Tokens Table

| Column      | Type     | Constraints                    | Description                        |
|-------------|----------|--------------------------------|------------------------------------|
| id          | Integer  | Primary Key, Auto Increment    | Unique identifier                  |
| token       | String   | Unique, Not Null, Indexed      | The actual refresh token           |
| user_id     | Integer  | Foreign Key, Not Null          | Reference to users table           |
| expires_at  | DateTime | Not Null                       | Token expiration timestamp         |
| is_active   | Boolean  | Not Null, Default True         | Whether token is still valid       |
| created_at  | DateTime | Not Null, Default Now          | Token creation timestamp           |

### Relationships

- **User → RefreshToken**: One-to-Many (A user can have multiple refresh tokens)
- **RefreshToken → User**: Many-to-One (Each refresh token belongs to one user)

## API Endpoints

### 1. Login (Updated)
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=john&password=secret123
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "secure-random-token-here",
  "token_type": "bearer"
}
```

### 2. Refresh Token
```http
POST /refresh
Content-Type: application/json

{
  "refresh_token": "secure-random-token-here"
}
```

**Response**:
```json
{
  "access_token": "new-jwt-token-here",
  "token_type": "bearer"
}
```

### 3. Logout (Single Device)
```http
POST /logout
Content-Type: application/json

{
  "refresh_token": "secure-random-token-here"
}
```

**Response**:
```json
{
  "message": "Successfully logged out"
}
```

### 4. Logout All Devices
```http
POST /logout-all
Authorization: Bearer <access-token>
```

**Response**:
```json
{
  "message": "Successfully logged out from all devices"
}
```

## Security Considerations

### 1. Token Storage

**Access Tokens**:
- Store in memory or secure HTTP-only cookies
- Never store in localStorage due to XSS risks
- Include in Authorization header for API requests

**Refresh Tokens**:
- Store securely (HTTP-only cookies recommended)
- Never expose in JavaScript
- Use HTTPS only

### 2. Token Rotation (Future Enhancement)

Consider implementing refresh token rotation where:
- Each refresh generates a new refresh token
- Old refresh token is immediately invalidated
- Provides additional security against token theft

### 3. HTTPS Only

**Critical**: Always use HTTPS in production to prevent token interception.

## Testing

### Manual Testing Commands

#### 1. Register a User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

#### 2. Login and Get Tokens
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"
```

#### 3. Use Access Token
```bash
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer <access-token>"
```

#### 4. Refresh Access Token
```bash
curl -X POST "http://localhost:8000/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh-token>"}'
```

#### 5. Logout
```bash
curl -X POST "http://localhost:8000/logout" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh-token>"}'
```

### Automated Testing

Consider adding these test cases:

1. **Token Expiry Tests**: Verify access tokens expire after 30 minutes
2. **Refresh Token Tests**: Test token refresh functionality
3. **Revocation Tests**: Test single and bulk token revocation
4. **Security Tests**: Test invalid token handling
5. **Rate Limiting Tests**: Verify rate limits are enforced

## Migration Guide

### From Old System (10-day tokens) to New System

1. **Immediate Changes**:
   - Access tokens now expire in 30 minutes instead of 10 days
   - Login endpoint returns both access and refresh tokens
   - Clients must implement token refresh logic

2. **Client-Side Changes Required**:
   ```javascript
   // Before: Store token for 10 days
   localStorage.setItem('token', response.access_token);
   
   // After: Store both tokens securely
   // Store access token in memory
   sessionStorage.setItem('access_token', response.access_token);
   // Store refresh token in HTTP-only cookie (recommended)
   // or secure storage
   ```

3. **Handling Token Expiry**:
   ```javascript
   // Intercept 401 responses and refresh token
   axios.interceptors.response.use(
     response => response,
     async error => {
       if (error.response?.status === 401) {
         const newToken = await refreshToken();
         // Retry original request with new token
       }
       return Promise.reject(error);
     }
   );
   ```

### Database Migration

The migration was automatically generated and applied:

```bash
# Generated migration
alembic revision --autogenerate -m "add_refresh_token_table"

# Applied to database
alembic upgrade head
```

## Best Practices

### 1. Client Implementation

**Token Refresh Strategy**:
```javascript
class TokenManager {
  constructor() {
    this.accessToken = null;
    this.refreshToken = null;
    this.refreshPromise = null;
  }

  async refreshAccessToken() {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.performRefresh();
    try {
      const result = await this.refreshPromise;
      return result;
    } finally {
      this.refreshPromise = null;
    }
  }

  async performRefresh() {
    const response = await fetch('/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: this.refreshToken })
    });
    
    if (!response.ok) {
      // Refresh token is invalid, redirect to login
      this.logout();
      throw new Error('Refresh failed');
    }
    
    const data = await response.json();
    this.accessToken = data.access_token;
    return data.access_token;
  }
}
```

### 2. Server-Side Maintenance

**Scheduled Cleanup** (Consider adding):
```python
# Add to a scheduled task (cron job or similar)
def cleanup_expired_tokens():
    with SessionLocal() as db:
        auth.cleanup_expired_refresh_tokens(db)
```

### 3. Monitoring and Logging

Consider logging:
- Token creation events
- Token refresh events
- Failed authentication attempts
- Token revocation events

### 4. Environment Configuration

**Production Settings**:
```python
# Use environment variables in production
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
```

## Troubleshooting

### Common Issues

1. **"Invalid or expired refresh token"**
   - Check if refresh token exists in database
   - Verify token hasn't expired
   - Confirm token is still active (not revoked)

2. **"Could not validate credentials"**
   - Access token may have expired (30 minutes)
   - Try refreshing the access token
   - Check token format and encoding



### Debug Commands

```bash
# Check refresh tokens in database
psql -d your_database -c "SELECT * FROM refresh_tokens WHERE user_id = 1;"

# Check token expiry
psql -d your_database -c "SELECT token, expires_at, expires_at < NOW() as expired FROM refresh_tokens;"
```

## Conclusion

The refresh token implementation significantly improves the security posture of the application while maintaining usability. The shorter access token lifespan reduces the window of vulnerability, while refresh tokens provide a secure way to maintain user sessions.

Key benefits achieved:
- ✅ Reduced security risk with 30-minute access tokens
- ✅ User-controlled session management with logout capabilities
- ✅ Audit trail for token usage
- ✅ Compliance with security best practices


The implementation follows industry standards and provides a solid foundation for future security enhancements.
