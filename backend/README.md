# Backend - AI Expense Import System

FastAPI backend for processing and normalizing expense data from Excel files.

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   Copy `.env.example` to `.env` and update with your credentials:
   ```bash
   cp .env.example .env
   ```

   Required variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to Firestore credentials JSON
   - `FIRESTORE_COLLECTION`: Firestore collection name (default: "expenses")
   - `GCP_BUCKET`: Google Cloud Storage bucket name

## Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python main.py
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Upload & Processing

- **POST /api/upload** - Upload and process Excel file
  - Form data: `file` (Excel file), `year` (4-digit year)
  - Returns: Import statistics

- **POST /api/preview** - Preview normalized data without saving
  - Form data: `file` (Excel file), `year` (4-digit year)
  - Returns: Preview of normalized data (first 10 rows)

### Expense Management

- **GET /api/expenses** - Get all years with data
- **GET /api/expenses/{year}** - Get expenses for a specific year
  - Query params: `limit` (max 1000, default 100)
- **GET /api/stats/{year}** - Get statistics for a year
- **DELETE /api/expenses/{year}** - Delete all expenses for a year

### Health Check

- **GET /** - API info
- **GET /health** - Health check

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── routers/
│   ├── upload_router.py   # File upload and processing endpoints
│   └── expense_router.py  # Expense query and management endpoints
├── services/
│   ├── ai_parser.py       # AI normalization using Gemini API
│   ├── firestore_service.py  # Firestore database operations
│   └── storage_service.py    # Google Cloud Storage operations
├── utils/
│   └── file_utils.py      # File handling utilities
├── tests/
│   ├── test_ai_parser.py
│   └── test_file_utils.py
├── requirements.txt
└── .env.example
```

## Features

- 📤 Excel file upload (`.xlsx`, `.xls`)
- 🧠 AI-powered data normalization using Gemini API
- 💾 Firestore integration for persistent storage
- ☁️ Google Cloud Storage for file backup
- 🔍 Query expenses by year
- 📊 Expense statistics and analytics
- ✅ Input validation and error handling
- 🧪 Unit tests included

## Notes

- Maximum file size: 5MB
- Supported formats: `.xlsx`, `.xls`
- Batch operations for efficient Firestore writes
- Fallback to mock normalization if Gemini API is unavailable
- CORS enabled for frontend integration
