# 🧠 Copilot Instruction Document: AI-Driven Expense Import System

## 🎯 Project Goal
You are an AI coding assistant tasked with creating a **full-stack application** to import yearly expense Excel sheets with differing formats, use AI (Gemini API) to normalize their data, and store them into a **Firestore database**.

---

## 🧩 Stack Overview

### Backend
- **Language:** Python  
- **Framework:** FastAPI  
- **AI Integration:** Google Gemini API (or placeholder function for now)  
- **Excel Parsing:** pandas, openpyxl  
- **Database:** Google Firestore (via google-cloud-firestore)  
- **Storage:** Google Cloud Storage for uploaded Excel files  
- **Authentication:** Firebase Admin SDK (optional)  
- **Environment Management:** .env + python-dotenv

### Frontend
- **Language:** TypeScript  
- **Framework:** React  
- **UI Library:** Material-UI (MUI v5)  
- **Build Tool:** Vite  
- **State Management:** React Query  
- **File Upload:** Axios + input[type="file"] + progress bar  
- **Deployment:** Firebase Hosting  

---

## 📁 Project Structure

```
ai-expense-import/
├── backend/
│   ├── main.py
│   ├── routers/
│   │   ├── upload_router.py
│   │   └── expense_router.py
│   ├── services/
│   │   ├── ai_parser.py
│   │   ├── firestore_service.py
│   │   └── storage_service.py
│   ├── utils/
│   │   └── file_utils.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUploader.tsx
│   │   │   ├── ExpensePreview.tsx
│   │   │   └── ImportSummary.tsx
│   │   ├── pages/
│   │   │   └── Dashboard.tsx
│   │   ├── api/
│   │   │   └── expenses.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── vite.config.ts
│   ├── package.json
│   └── tsconfig.json
│
└── README.md
```

---

## 🚀 Backend Implementation Instructions (FastAPI)

1. **Initialize project**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn pandas openpyxl google-cloud-firestore google-cloud-storage python-dotenv httpx python-multipart pytest pytest-asyncio
   ```

2. **Database Abstraction Layer**
   - `db_factory.py` - Automatically selects SQLite (dev) or Firestore (prod)
   - `services/sqlite_db.py` - SQLite implementation
   - `services/firestore_db.py` - Firestore implementation
   - Both implement the same interface for seamless switching

2. **Create `.env`**
   ```
   ENVIRONMENT=development
   SECRET_KEY=your-32-byte-hex-key
   GEMINI_API_KEY=your_api_key_here
   # For production only:
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   FIRESTORE_COLLECTION=expenses
   GCP_BUCKET=expense-uploads
   ```

3. **`main.py`**
   - Initialize FastAPI
   - Include routers
   - Add CORS middleware for React

4. **`upload_router.py`**
   - Endpoint: `POST /upload`
   - Accept Excel file upload
   - Save temporarily or directly to Cloud Storage
   - Extract sheet data via `pandas.read_excel()`
   - Send extracted rows to `ai_parser.normalize_expense_data()`
   - Store returned JSON into database via `db.save_expenses()` (uses db_factory)

5. **`ai_parser.py`**
   - Function `normalize_expense_data(raw_data: list[dict]) -> list[dict]`
   - Calls Gemini API to interpret mixed-column Excel sheets
   - Returns unified format:
     ```json
     { "date": "2024-01-03", "category": "Transport", "description": "Taxi", "amount": 35.0 }
     ```

6. **`db_factory.py`**
   - Reads `ENVIRONMENT` variable
   - Returns `SQLiteDatabase()` for development
   - Returns `FirestoreDatabase()` for production
   - Provides common interface: `save_expenses()`, `get_expenses_by_year()`, etc.

7. **`sqlite_db.py`** and **`firestore_db.py`**
   - Both implement identical interface
   - SQLite: Local file storage (expenses.db)
   - Firestore: Cloud NoSQL database
   - Seamless switching without code changes

7. **`storage_service.py`**
   - Handles upload/download to Google Cloud Storage

8. **`file_utils.py`**
   - Helper to safely handle temp files and validate Excel extensions

---

## ⚛️ Frontend Implementation Instructions (React + TypeScript)

1. **Initialize**
   ```bash
   cd frontend
   npm create vite@latest . -- --template react-ts
   npm install @mui/material @emotion/react @emotion/styled axios react-query
   ```

2. **`FileUploader.tsx`**
   - File input with progress bar
   - On submit → POST to `/upload` (backend)
   - Show spinner and handle success/failure

3. **`ExpensePreview.tsx`**
   - Displays returned normalized data before confirming import

4. **`ImportSummary.tsx`**
   - Shows how many records were imported successfully

5. **`expenses.ts`**
   - Axios client configured with base URL of backend (e.g. `http://localhost:8000`)

6. **`Dashboard.tsx`**
   - Central page with file upload, preview, and import summary flow

---

## 🧪 Testing

**Backend Tests (pytest):**
- `tests/test_ai_parser.py`: validate mock Gemini output normalization  
- `tests/test_upload_router.py`: check Excel parsing and Firestore write  

**Frontend Tests (Vitest or Jest):**
- Snapshot test for file upload component  
- Integration test mocking backend with MSW  

---

## ☁️ Deployment

### Backend
- Deploy as **Cloud Run service** or **Firebase Function**
- Enable Firestore + Storage API

### Frontend
- Build using `npm run build`
- Deploy with Firebase Hosting:
  ```bash
  firebase deploy --only hosting
  ```

---

## 🧠 Copilot Prompts to Use

**Prompt 1:**  
> Create FastAPI endpoints in `/backend/routers/upload_router.py` that handle Excel file upload, parse using pandas, call AI parser, and save normalized data to Firestore.

**Prompt 2:**  
> Implement `ai_parser.py` to call Gemini API and normalize mixed-format expense data to `{date, category, description, amount}`.

**Prompt 3:**  
> Build React components for file upload and preview of normalized data in `/frontend/src/components/`.

**Prompt 4:**  
> Create Firestore integration code with proper error handling and batch writes.
