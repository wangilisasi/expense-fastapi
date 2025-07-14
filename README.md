# 💰 Expense Tracker API

A robust FastAPI-based expense tracking application with PostgreSQL database integration. Track your expenses across multiple budgets with detailed categorization and reporting.

## 🚀 Features

- **Multiple Expense Trackers**: Create and manage multiple budget trackers with start/end dates
- **Expense Management**: Add, view, and delete expenses with detailed descriptions
- **Automatic Relationships**: Expenses are automatically linked to their respective trackers
- **Robust Database Connection**: SSL-enabled PostgreSQL with connection pooling and retry logic
- **RESTful API**: Clean, well-documented API endpoints
- **Production Ready**: Deployed on Railway with proper error handling

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Deployment**: Railway
- **Server**: Hypercorn ASGI server
- **Validation**: Pydantic schemas

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/wangilisasi/expense-fastapi.git
   cd expense-fastapi
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker
   ```

5. **Run the application**
   ```bash
   hypercorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Expense Trackers

#### Get All Trackers
```http
GET /trackers
```
Returns a list of all expense trackers.

#### Create New Tracker
```http
POST /trackers
Content-Type: application/json

{
  "name": "Monthly Budget",
  "description": "January 2024 expenses",
  "startDate": "2024-01-01",
  "endDate": "2024-01-31",
  "budget": 1500.00
}
```

#### Get Tracker Details
```http
GET /trackers/{id}
```
Returns tracker details including all associated expenses.

### Expenses

#### Get Expenses for Tracker
```http
GET /trackers/{trackerId}/expenses
```
Returns all expenses for a specific tracker.

#### Add New Expense
```http
POST /expenses
Content-Type: application/json

{
  "description": "Grocery shopping",
  "amount": 85.50,
  "date": "2024-01-15",
  "trackerId": 1
}
```

#### Delete Expense
```http
DELETE /expenses/{id}
```
Removes an expense by ID.

## 🗄️ Database Schema

### ExpenseTracker Table
- `id` (Primary Key)
- `name` (String, required)
- `description` (String, optional)
- `startDate` (Date, required)
- `endDate` (Date, required)
- `budget` (Float, required)

### Expense Table
- `id` (Primary Key)
- `description` (String, required)
- `amount` (Float, required)
- `date` (Date, required)
- `trackerId` (Foreign Key → ExpenseTracker.id)

## 🔧 Recent Improvements

### Database Connection Fixes
- **SSL Connection Handling**: Proper SSL configuration for PostgreSQL
- **Connection Pooling**: Implemented connection pooling with health checks
- **Retry Logic**: Automatic retry mechanism for transient database failures
- **Connection Recycling**: Prevents stale connections with 5-minute recycling

### Error Handling
- Graceful handling of database connection errors
- User-friendly error messages
- Automatic rollback on failed transactions

## 🚀 Deployment

This application is deployed on [Railway](https://railway.app) with the following configuration:

- **Builder**: Nixpacks
- **Start Command**: `hypercorn main:app --bind "[::]:$PORT"`
- **Environment**: PostgreSQL database with SSL enabled

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (automatically provided by Railway)

## 📁 Project Structure

```
expense-fastapi/
├── app/
│   ├── __init__.py
│   ├── database.py      # Database configuration and connection
│   ├── models.py        # SQLAlchemy models
│   └── schemas.py       # Pydantic schemas
├── main.py              # FastAPI application and routes
├── requirements.txt     # Python dependencies
├── railway.json         # Railway deployment config
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- **Live API**: [Deployed on Railway](https://expense-fastapi-production.up.railway.app)
- **API Documentation**: Access `/docs` endpoint for interactive Swagger UI
- **Repository**: [GitHub](https://github.com/wangilisasi/expense-fastapi)

---

Built with ❤️ using FastAPI and PostgreSQL
