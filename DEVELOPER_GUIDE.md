# Smart Expense Importer - Complete Developer Guide

**Version 1.0.0** | **Last Updated:** November 10, 2025

A comprehensive guide for developers to understand, develop, and deploy the Smart Expense Importer application.

---

## 📑 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Quick Start](#2-quick-start)
3. [Architecture](#3-architecture)
4. [Database Abstraction Layer](#4-database-abstraction-layer)
5. [Local Development Setup](#5-local-development-setup)
6. [Technology Stack](#6-technology-stack)
7. [Feature Documentation](#7-feature-documentation)
8. [API Reference](#8-api-reference)
9. [Google Cloud Deployment](#9-google-cloud-deployment)
10. [Troubleshooting](#10-troubleshooting)
11. [Maintenance](#11-maintenance)

---

## 1. Project Overview

Smart Expense Importer is a production-ready web application for importing and managing multi-year expense data from Excel files with:

- **AI-Powered Parsing** (Google Gemini API) - Handles varying Excel formats
- **Database Abstraction** (SQLite for dev, Firestore for prod)
- **Secure Cloud Storage** (Google Cloud Storage for file backups)
- **Modern Stack** (FastAPI + React + TypeScript)
- **Automatic Environment Switching** (dev/prod databases)

### Key Features

- ✅ Upload Excel files with varying column structures
- ✅ AI normalization to standard format
- ✅ Preview data before importing
- ✅ Year-based expense organization
- ✅ Advanced search and filtering
- ✅ Statistics and analytics per year
- ✅ Automatic environment detection (SQLite ↔ Firestore)

---

## 2. Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Local Development (2 minutes)

**Backend Setup:**

```powershell
# Clone and setup backend
cd Expense-data-automation\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
@"
ENVIRONMENT=development
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
GEMINI_API_KEY=your_gemini_api_key
"@ | Out-File .env -Encoding utf8

# Run backend (or press F5 in VS Code)
uvicorn main:app --reload
```

**Frontend Setup:**

```powershell
# Setup frontend (new terminal)
cd ..\frontend
npm install

# Create .env.development
@"
VITE_API_BASE_URL=http://localhost:8000/api
"@ | Out-File .env.development -Encoding utf8

npm run dev
```

**Access:** http://localhost:5173

### Deploy to Cloud (FREE)

```powershell
.\deploy-to-gcp.ps1
```

---

## 3. Architecture

### System Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│  React Frontend │──────▶│  FastAPI Backend │──────▶│    Database      │
│  (TypeScript)   │       │    (Python)      │       │  SQLite (dev)    │
└─────────────────┘       └─────────────────┘       │  Firestore (prod)│
                                 │                   └──────────────────┘
                                 │
                          ┌──────▼──────────┐
                          │  Gemini API     │
                          │  (AI Parser)    │
                          └─────────────────┘
```

### Database Abstraction

The app uses `db_factory.py` to automatically select the right database:

- `ENVIRONMENT=development` → SQLite (local file)
- `ENVIRONMENT=production` → Firestore (Google Cloud)

All API endpoints use the same interface regardless of database.

---

## 4. Database Abstraction Layer

### How It Works

```
db_factory.py         - Returns appropriate database instance
sqlite_db.py          - SQLite implementation
firestore_db.py       - Firestore implementation
```

**Example:**

```python
# db_factory.py
def get_database():
    environment = os.getenv("ENVIRONMENT", "production")
    if environment == "development":
        return SQLiteDatabase()
    else:
        return FirestoreDatabase()

db = get_database()
```

### Usage in API Endpoints

```python
from db_factory import db

@router.get("/expenses/{year}")
async def get_expenses(year: str):
    return await db.get_expenses_by_year(year)
```

### Common Interface

Both databases provide identical methods:

- `save_expenses()` - Import expense data
- `get_expenses_by_year()` - Retrieve expenses for a year
- `get_all_years()` - List all years with data
- `get_year_statistics()` - Get analytics for a year
- `delete_expenses_by_year()` - Delete year data
- `search_expenses()` - Search with filters

### Data Migration

**Export from Firestore to JSON:**

```python
# Create migration script: export_data.py
from services.firestore_db import FirestoreDatabase
import json

async def export():
    db = FirestoreDatabase()
    years = await db.get_all_years()
    
    for year in years:
        expenses = await db.get_expenses_by_year(year)
        with open(f"data_{year}.json", "w") as f:
            json.dump(expenses, f, indent=2)

# Run: python export_data.py
```

**Import to SQLite:**

```python
# Create migration script: import_to_sqlite.py
from services.sqlite_db import SQLiteDatabase
import json

async def import_data(year, filename):
    db = SQLiteDatabase()
    with open(filename) as f:
        expenses = json.load(f)
    await db.save_expenses(year, expenses, filename)

# Run: python import_to_sqlite.py
```

---

## 5. Local Development Setup

### Backend Setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Create `.env`:**

```bash
ENVIRONMENT=development
SECRET_KEY=your-32-byte-hex-key
GEMINI_API_KEY=your-gemini-key
```

**Run:**

```powershell
uvicorn main:app --reload
# Or press F5 in VS Code
```

### Frontend Setup

```powershell
cd frontend
npm install
```

**Create `.env.development`:**

```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

**Run:**

```powershell
npm run dev
```

### First Time Use

1. Open http://localhost:5173
2. Upload an Excel file with expense data
3. Preview normalized results
4. Confirm and import
5. View expenses in dashboard

---

## 6. Technology Stack

**Backend:**

- FastAPI - Web framework
- SQLite - Development database
- Firestore - Production database
- Google Gemini - AI parsing
- Pandas - Excel processing
- Docker - Containerization

**Frontend:**

- React 18 - UI framework
- TypeScript - Type safety
- Material-UI - Components
- Vite - Build tool
- Axios - HTTP client

**Cloud:**

- Cloud Run - Backend hosting
- Firestore - NoSQL database
- Cloud Storage - File storage
- Cloud Build - CI/CD

---

## 7. Feature Documentation

### 7.1 Excel File Upload

**Supported Formats:**
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

**Process Flow:**

1. User uploads Excel file + year
2. Backend validates file format
3. Pandas extracts all rows
4. Sample rows sent to Gemini API
5. AI returns normalized data
6. Data saved to database
7. File backed up to Cloud Storage (prod only)

### 7.2 AI Normalization

**How it works:**

The AI parser identifies columns regardless of naming:

```
Input (Excel):           Output (Normalized):
┌─────────┬─────────┐    ┌────────────┬──────────┬────────┐
│ Date    │ Expense │    │ date       │ category │ amount │
│ Jan 5   │ 120.50  │ →  │ 2023-01-05 │ Office   │ 120.50 │
│ Taxi    │ 35      │    │ 2023-01-06 │ Travel   │ 35.00  │
└─────────┴─────────┘    └────────────┴──────────┴────────┘
```

**Supported Fields:**
- `date` (auto-formatted to YYYY-MM-DD)
- `category` (auto-categorized)
- `description` (extracted from context)
- `amount` (normalized to float)

**Model:** `gemini-2.0-flash-exp`

**Cost:** FREE (within daily limits)

### 7.3 Preview Mode

Test AI parsing without saving to database:

```
POST /api/preview
- Processes first 10 rows only
- Returns normalized preview
- No database writes
```

### 7.4 Statistics & Analytics

Per-year statistics include:

- Total expenses count
- Total amount
- Category breakdown (count + total)
- Monthly breakdown (count + total)

### 7.5 Search & Filtering

Advanced search with filters:

- Year
- Category
- Date range (from/to)
- Amount range (min/max)

---

## 8. API Reference

### Authentication

Currently public endpoints. For production, add JWT authentication (see Leave Tracker guide).

### File Upload

**Upload & Import:**

```http
POST /api/upload
Content-Type: multipart/form-data

file: [Excel file]
year: "2023"

Response:
{
  "imported": 124,
  "skipped": 3,
  "status": "ok"
}
```

**Preview Only:**

```http
POST /api/preview
Content-Type: multipart/form-data

file: [Excel file]
year: "2023"

Response:
{
  "status": "ok",
  "total_rows": 150,
  "preview_rows": 10,
  "data": [...]
}
```

### Expenses

**Get by Year:**

```http
GET /api/expenses/{year}?limit=100

Response:
{
  "status": "ok",
  "year": "2023",
  "count": 124,
  "expenses": [...]
}
```

**List All Years:**

```http
GET /api/expenses

Response:
{
  "status": "ok",
  "years": ["2024", "2023", "2022"],
  "count": 3
}
```

**Delete Year:**

```http
DELETE /api/expenses/{year}

Response:
{
  "status": "ok",
  "deleted": 124,
  "message": "Deleted 124 expenses from 2023"
}
```

### Statistics

```http
GET /api/stats/{year}

Response:
{
  "status": "ok",
  "year": "2023",
  "total_expenses": 124,
  "total_amount": 15234.50,
  "by_category": [...],
  "by_month": [...]
}
```

### Search

```http
GET /api/search?year=2023&category=Travel&min_amount=50

Response:
{
  "status": "ok",
  "count": 15,
  "expenses": [...]
}
```

### Interactive Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 9. Google Cloud Deployment

### Prerequisites

```powershell
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Enable Required APIs

```powershell
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Deploy Backend (Cloud Run)

```powershell
cd backend

# Build and push Docker image
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/expense-repo/backend:latest

# Deploy to Cloud Run
gcloud run deploy expense-importer-api `
  --image us-central1-docker.pkg.dev/PROJECT_ID/expense-repo/backend:latest `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars ENVIRONMENT=production,GEMINI_API_KEY=your_key
```

### Deploy Frontend (Cloud Storage)

```powershell
cd frontend

# Build
npm run build

# Create bucket
gsutil mb gs://expense-importer-frontend

# Upload
gsutil -m cp -r dist/* gs://expense-importer-frontend/

# Make public
gsutil iam ch allUsers:objectViewer gs://expense-importer-frontend

# Configure as website
gsutil web set -m index.html gs://expense-importer-frontend
```

### Setup Firestore

```powershell
# Create Firestore database (Native mode)
gcloud firestore databases create --region=us-central1
```

### Cost Estimate

**FREE for small/medium usage:**

- Cloud Run: 2M requests/month
- Firestore: 50K reads, 20K writes/day
- Storage: 5GB + 1GB egress/month
- Gemini API: 15 req/min, 1M tokens/day

**Expected:** $0-5/month within free tier

---

## 10. Troubleshooting

### Backend Won't Start

- Check Python 3.10+
- Activate venv
- Install requirements
- Verify `.env` exists with required variables
- Check `ENVIRONMENT` variable

### Database Connection Error

**SQLite:**
- Ensure `ENVIRONMENT=development`
- Check write permissions in project directory

**Firestore:**
- Check `GOOGLE_APPLICATION_CREDENTIALS` path
- Verify service account key is valid
- Ensure Firestore API is enabled

### AI Parser Fails

- Set `GEMINI_API_KEY` in `.env`
- Restart backend
- Verify key at https://aistudio.google.com/
- Check model is `gemini-2.0-flash-exp`
- Review rate limits (15 req/min free tier)

### Excel Parsing Error

- Ensure file is valid Excel format (`.xlsx` or `.xls`)
- Check file isn't password-protected
- Verify file isn't corrupted
- Try opening in Excel first

### Frontend Shows Old Version

- Clear browser cache (`Ctrl+Shift+Delete`)
- Use incognito mode
- Hard refresh (`Ctrl+F5`)

### CORS Errors

- Verify frontend URL in backend `main.py` CORS settings
- Check `VITE_API_BASE_URL` in frontend `.env`

---

## 11. Maintenance

### Regular Tasks

**Weekly:**
- Check logs for errors
- Monitor free tier usage

**Monthly:**
- Update dependencies
- Review security advisories

**Quarterly:**
- Full dependency updates
- Security audit

### Updating Dependencies

**Backend:**

```powershell
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

**Frontend:**

```powershell
npm outdated
npm update package-name
npm update
```

### Backup & Restore

**Backup (Export from Firestore):**

```python
# Create: export_firestore.py
from services.firestore_db import FirestoreDatabase
import json

db = FirestoreDatabase()
# ... (see section 4)
```

**Restore to SQLite:**

```python
# Create: import_to_sqlite.py
# ... (see section 4)
```

### Version Control

**Commit Format:**

```
feat: Add expense search functionality
fix: Resolve AI parsing timeout
docs: Update developer guide
chore: Update dependencies
```

---

## Quick Reference

### Development Commands

```powershell
# Backend
cd backend; uvicorn main:app --reload

# Frontend
cd frontend; npm run dev

# Build
npm run build

# Tests
cd backend; pytest
```

### Environment Variables

**Backend `.env`:**

```bash
ENVIRONMENT=development|production
SECRET_KEY=32-byte-hex
GEMINI_API_KEY=your-key
GOOGLE_APPLICATION_CREDENTIALS=firestore-key.json  # prod only
FIRESTORE_COLLECTION=expenses
GCP_BUCKET=expense-uploads
```

**Frontend `.env.development`:**

```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

### Useful Links

- **Gemini API:** https://aistudio.google.com/apikey
- **GCP Console:** https://console.cloud.google.com
- **FastAPI:** https://fastapi.tiangolo.com
- **React:** https://react.dev
- **Material-UI:** https://mui.com

---

## Summary

**Status:** Production Ready  
**Version:** 1.0.0  
**Cost:** $0/month (free tier)  
**Updated:** November 10, 2025

This guide provides everything needed to develop and deploy the Smart Expense Importer. For questions or issues, check the troubleshooting section or create a GitHub issue.

---

## Additional Resources

- [README.md](./README.md) - Project overview
- [INSTRUCTIONS_FOR_COPILOT.md](./INSTRUCTIONS_FOR_COPILOT.md) - AI assistant guide
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Technical details

---

**Happy Coding! 🚀**
