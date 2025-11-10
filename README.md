# 💰 Smart Expense Importer (AI + Firestore)

## 📘 Overview

**Smart Expense Importer** is an intelligent tool that lets you upload yearly Excel files of expenses — even if each year’s file has a slightly different structure — and automatically extracts, normalizes, and stores the data in **Google Firestore**.

This system uses an AI model (Gemini, GPT, or any LLM) to understand column meanings, normalize inconsistent formats, and ensure your multi-year expense history lives in a single, searchable, and centralized system.

---

## ✨ Key Features

- 📂 Upload Excel files for any year (`.xlsx`, `.xls`)
- 🧠 AI-based column mapping (handles format variations between years)
- 🔍 Preview and confirm parsed results before importing
- ☁️ Centralized data stored in **Firestore**
- 📊 Year-wise expense visualization (optional future enhancement)
- 🔁 Duplicate detection and data validation
- ⚡ Cloud-ready (Firebase Functions or Node/Express backend)

---

## 🏗️ Architecture

```
Frontend (React)
│
├── File Upload (Excel)
│       ↓
│   POST /upload-expense
│
Backend (Node.js / Python)
│
├── Excel Parser (pandas / exceljs)
├── AI Normalizer (Gemini API)
├── Firestore Writer
│
Database (Firestore)
└── /expenses/{year}/{expense_id}
```

---

## 📁 Project Structure

```
Expense-data-automation/
├── backend/                   # FastAPI Python Backend
│   ├── main.py               # Main API server
│   ├── routers/
│   │   ├── upload_router.py  # File upload endpoints
│   │   └── expense_router.py # Expense management endpoints
│   ├── services/
│   │   ├── ai_parser.py      # AI normalization with Gemini API
│   │   ├── firestore_service.py  # Firestore operations
│   │   └── storage_service.py    # Google Cloud Storage
│   ├── utils/
│   │   └── file_utils.py     # File handling utilities
│   ├── tests/                # Unit tests
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                  # React TypeScript Frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── expenses.ts   # API client
│   │   ├── components/
│   │   │   ├── FileUploader.tsx
│   │   │   ├── ExpensePreview.tsx
│   │   │   └── ImportSummary.tsx
│   │   ├── pages/
│   │   │   └── Dashboard.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── .env.example
│
├── INSTRUCTIONS_FOR_COPILOT.md
└── README.md
```

---

## 🚀 Quick Start

### Backend Setup (SQLite - No Cloud Required!)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env - set ENVIRONMENT=development
   # Add your GEMINI_API_KEY (get from https://aistudio.google.com/apikey)
   ```

5. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

   Backend API will be available at `http://localhost:8000`  
   API documentation at `http://localhost:8000/docs`
   
   **Note:** In development mode, all data is stored in a local `expenses.db` SQLite file.

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Default backend URL is already set to http://localhost:8000/api
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

---

## ⚙️ Environment Variables

### Backend (.env)
```bash
# Environment: development (uses SQLite) or production (uses Firestore)
ENVIRONMENT=development

# Secret key for session management
SECRET_KEY=your-32-byte-hex-key-here

# AI Service
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud (only needed for ENVIRONMENT=production)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-credentials.json
FIRESTORE_COLLECTION=expenses
GCP_BUCKET=expense-uploads
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

### 🔄 Database Abstraction

The application automatically switches between databases based on the `ENVIRONMENT` variable:

- **`ENVIRONMENT=development`** → Uses **SQLite** (local file, no cloud credentials needed)
- **`ENVIRONMENT=production`** → Uses **Firestore** (requires Google Cloud setup)

This means you can develop locally without setting up Google Cloud, and seamlessly deploy to production with Firestore.

---

## 📚 API Documentation

Full API documentation is available at `http://localhost:8000/docs` when running the backend.

### Main Endpoints

- **POST /api/upload** - Upload and process Excel file
- **POST /api/preview** - Preview normalized data without saving
- **GET /api/expenses** - Get all years with data
- **GET /api/expenses/{year}** - Get expenses for a specific year
- **GET /api/stats/{year}** - Get statistics for a year
- **DELETE /api/expenses/{year}** - Delete all expenses for a year

## 🔍 Example API Flow

### POST `/api/upload`
**Description:** Accepts an Excel file and the corresponding year.

#### Request
- **Form Data:**
  - `file`: Excel file
  - `year`: Year (e.g., `2023`)

#### Process Flow
1. Parse Excel into raw JSON using `exceljs` or `pandas`.
2. Send parsed sample rows to Gemini:
   ```json
   {
     "rows": [
       { "Spending": "Jan 5", "Details": "Office supplies", "RM": "120.50" },
       { "Spending": "Jan 6", "Details": "Taxi", "RM": "35" }
     ],
     "instruction": "Map to fields {date, category, description, amount}."
   }
   ```
3. Gemini returns normalized rows:
   ```json
   [
     { "date": "2023-01-05", "category": "Office", "description": "Office supplies", "amount": 120.50 },
     { "date": "2023-01-06", "category": "Transport", "description": "Taxi", "amount": 35.00 }
   ]
   ```
4. Backend validates and saves each entry into:
   ```
   /expenses/2023/{auto_id}
   ```

#### Response
```json
{
  "imported": 124,
  "skipped": 3,
  "status": "ok"
}
```

---

## 🧠 AI Mapping Logic (Gemini Prompt Example)

```text
You are an expert data normalizer. 
Given an array of rows from an Excel sheet representing expenses, 
detect which columns represent {date, category, description, amount}, 
standardize the output to this JSON format:

[
  { "date": "YYYY-MM-DD", "category": "...", "description": "...", "amount": float }
]

Only output JSON. Assume the provided 'year' if the date is missing the year.
```

---

## 🧩 Firestore Data Model

```json
{
  "date": "2023-01-05",
  "category": "Office",
  "description": "Printer ink",
  "amount": 120.50,
  "source_file": "expenses_2023.xlsx",
  "imported_at": "2025-11-10T09:00:00Z"
}
```

**Collection Path:**  
`/expenses/{year}/{document_id}`

---

## 🖥️ Frontend Features (React)

- Drag-and-drop Excel upload (`FileUpload.tsx`)
- Upload progress bar
- Table preview of normalized data
- Confirmation modal before import
- Year selector & filtering (in Dashboard)
- Toast notifications for success/errors

---

## 🚀 Deployment Options

| Environment | Suggested Tech | Notes |
|--------------|----------------|-------|
| Cloud        | Firebase Functions | Ideal if using Firestore |
| Server       | Node.js + Express | Deploy on Render, Vercel, or GCP |
| Local        | Docker Compose | For development |

---

## 🔒 Security Notes

- Validate Excel file types before upload
- Sanitize AI outputs (e.g., ensure `amount` is numeric)
- Limit file size (e.g., 5MB)
- Use Firestore security rules to limit write access

---

## 📊 Future Enhancements

- AI-powered **expense categorization**
- Dashboard with monthly/annual charts
- Duplicate detection
- Google Sheets sync
- Multi-user support with Firebase Auth

---

## 🧑‍💻 Contributing

1. Fork this repository
2. Create a new branch (`feature/xyz`)
3. Commit and push your changes
4. Open a Pull Request

---

## 📄 License

MIT License © 2025 — Smart Expense Importer Project

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test  # After setting up Vitest
```

---

## 📝 Development Notes

- Backend uses FastAPI with Python 3.10+
- Frontend built with React 18 + TypeScript + Vite
- AI normalization powered by Google Gemini API
- Data stored in Google Firestore
- File backups in Google Cloud Storage
- Material-UI for frontend components
- Full CORS support for local development

---
