# API Test Commands

All commands below already use your deployed API at `https://web-production-8c12.up.railway.app`.

## 1. Unauthenticated User Tests

### Try to access protected endpoint without authentication
```bash
curl -X GET "https://web-production-8c12.up.railway.app/trackers" \
  -H "Content-Type: application/json"
```

### Try to get current user info without authentication
```bash
curl -X GET "https://web-production-8c12.up.railway.app/me" \
  -H "Content-Type: application/json"
```

### Try to create a tracker without authentication
```bash
curl -X POST "https://web-production-8c12.up.railway.app/trackers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tracker",
    "description": "This should fail",
    "startDate": "2025-07-01",
    "endDate": "2025-07-31",
    "budget": 1500.00
  }'
```

## 2. Authenticated User Tests

### Step 1: Register a new user
```bash
curl -X POST "https://web-production-8c12.up.railway.app/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### Step 2: Login to get access token
```bash
curl -X POST "https://web-production-8c12.up.railway.app/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"
```

### Step 3: Get current user info (replace YOUR_TOKEN with token from login)
```bash
curl -X GET "https://web-production-8c12.up.railway.app/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 4: Create a tracker (authenticated)
```bash
curl -X POST "https://web-production-8c12.up.railway.app/trackers" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My First Tracker",
    "description": "Tracking my daily expenses",
    "startDate": "2025-07-01",
    "endDate": "2025-07-31",
    "budget": 1500.00
  }'
```

### Step 5: Get all trackers
```bash
curl -X GET "https://web-production-8c12.up.railway.app/trackers" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 6: Add an expense (replace TRACKER_ID with actual tracker ID from step 4)
```bash
curl -X POST "https://web-production-8c12.up.railway.app/expenses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "trackerId": TRACKER_ID,
    "description": "Coffee",
    "amount": 4.50,
    "date": "2024-01-15"
  }'
```

### Step 7: Get expenses for a tracker
```bash
curl -X GET "https://web-production-8c12.up.railway.app/trackers/TRACKER_ID/expenses" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 8: Get tracker details with expenses
```bash
curl -X GET "https://web-production-8c12.up.railway.app/trackers/TRACKER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Expected Responses

### Unauthenticated requests should return:
```json
{
  "detail": "Not authenticated"
}
```

### Successful registration should return:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com"
}
```

### Successful login should return:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
``` 