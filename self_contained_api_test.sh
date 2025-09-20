#!/bin/bash

# Self-contained curl script for Expense Tracker API
# This script will: 1) Login to get bearer token, 2) Get first tracker, 3) Query expenses for that tracker

# Configuration
API_BASE_URL="https://web-production-8c12.up.railway.app"
USERNAME="testuser"
PASSWORD="testpassword123"

echo "🚀 Starting Expense Tracker API Test..."
echo "=================================="

# Step 1: Login to get bearer token
echo "📝 Step 1: Logging in to get bearer token..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD")

echo "Login Response: $LOGIN_RESPONSE"

# Extract access token from response
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get access token. Response: $LOGIN_RESPONSE"
    echo ""
    echo "💡 If user doesn't exist, register first with:"
    echo "curl -X POST \"$API_BASE_URL/register\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{"
    echo "    \"username\": \"$USERNAME\","
    echo "    \"email\": \"test@example.com\","
    echo "    \"password\": \"$PASSWORD\""
    echo "  }'"
    exit 1
fi

echo "✅ Successfully obtained access token: ${ACCESS_TOKEN:0:20}..."
echo ""

# Step 2: Get all trackers
echo "📊 Step 2: Getting user's trackers..."
TRACKERS_RESPONSE=$(curl -s -X GET "$API_BASE_URL/trackers" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Trackers Response: $TRACKERS_RESPONSE"

# Extract first tracker UUID
TRACKER_UUID=$(echo $TRACKERS_RESPONSE | grep -o '"uuid_id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$TRACKER_UUID" ]; then
    echo "❌ No trackers found. Creating a sample tracker first..."
    
    # Create a sample tracker
    CREATE_TRACKER_RESPONSE=$(curl -s -X POST "$API_BASE_URL/trackers" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d '{
        "name": "Sample Tracker",
        "description": "Auto-created for API test",
        "startDate": "2025-01-01",
        "endDate": "2025-01-31",
        "budget": 1000.00
      }')
    
    echo "Created tracker: $CREATE_TRACKER_RESPONSE"
    
    # Extract UUID from created tracker
    TRACKER_UUID=$(echo $CREATE_TRACKER_RESPONSE | grep -o '"uuid_id":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$TRACKER_UUID" ]; then
        echo "❌ Failed to create tracker. Exiting."
        exit 1
    fi
    
    # Add a sample expense to the tracker
    echo "💰 Adding sample expense to tracker..."
    ADD_EXPENSE_RESPONSE=$(curl -s -X POST "$API_BASE_URL/expenses" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"uuid_tracker_id\": \"$TRACKER_UUID\",
        \"description\": \"Sample Coffee\",
        \"amount\": 4.50,
        \"date\": \"2025-01-15\"
      }")
    
    echo "Added expense: $ADD_EXPENSE_RESPONSE"
    echo ""
fi

echo "✅ Using tracker UUID: $TRACKER_UUID"
echo ""

# Step 3: Query expenses for that tracker
echo "💸 Step 3: Getting expenses for tracker $TRACKER_UUID..."
EXPENSES_RESPONSE=$(curl -s -X GET "$API_BASE_URL/trackers/$TRACKER_UUID/expenses" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Expenses Response: $EXPENSES_RESPONSE"
echo ""

# Bonus: Get tracker details with expenses
echo "🔍 Bonus: Getting detailed tracker information..."
TRACKER_DETAILS_RESPONSE=$(curl -s -X GET "$API_BASE_URL/trackers/$TRACKER_UUID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Tracker Details Response: $TRACKER_DETAILS_RESPONSE"
echo ""

# Bonus: Get tracker stats
echo "📈 Bonus: Getting tracker statistics..."
TRACKER_STATS_RESPONSE=$(curl -s -X GET "$API_BASE_URL/trackers/$TRACKER_UUID/stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Tracker Stats Response: $TRACKER_STATS_RESPONSE"
echo ""

echo "✅ All operations completed successfully!"
echo "=================================="
echo ""
echo "🔗 Summary of what was executed:"
echo "1. POST $API_BASE_URL/login (to get bearer token)"
echo "2. GET $API_BASE_URL/trackers (to get user's trackers)"
echo "3. GET $API_BASE_URL/trackers/$TRACKER_UUID/expenses (to query expenses)"
echo "4. GET $API_BASE_URL/trackers/$TRACKER_UUID (tracker details)"
echo "5. GET $API_BASE_URL/trackers/$TRACKER_UUID/stats (tracker statistics)"
