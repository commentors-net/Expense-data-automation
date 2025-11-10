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
smart-expense-importer/
├── backend/
│   ├── app.js                # Main API server (Express or FastAPI)
│   ├── services/
│   │   ├── excelParser.js    # Extracts tabular data from Excel
│   │   ├── aiMapper.js       # Sends extracted data to Gemini API for normalization
│   │   ├── firestore.js      # Handles writes/reads to Firestore
│   └── .env.example          # API keys, Firestore credentials
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── ExpensePreviewTable.tsx
│   │   └── pages/
│   │       └── Dashboard.tsx
│   └── package.json
│
└── README.md
```

---

## ⚙️ Backend Setup

### 1. Requirements
- Node.js 20+ (or Python 3.10+)
- Firestore project set up (Firebase)
- Gemini (Google AI Studio) API key

### 2. Environment Variables (`.env`)
```bash
GEMINI_API_KEY=your_gemini_key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/firestore-service-account.json
```

### 3. Install & Run
```bash
cd backend
npm install
npm start
```

---

## 🔍 Example API Flow

### POST `/upload-expense`
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

## 🧩 Example Screenshot (Concept)
*(To be added once frontend UI is implemented)*

---
