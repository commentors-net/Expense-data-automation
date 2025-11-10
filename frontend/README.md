# Frontend - AI Expense Import System

React + TypeScript frontend for the Smart Expense Importer.

## Features

- 📤 Drag-and-drop Excel file upload
- 👁️ Preview normalized data before import
- 📊 Real-time upload progress
- 📈 Import summary with statistics
- 💅 Modern UI with Material-UI
- 🎨 Responsive design

## Tech Stack

- **Framework:** React 18
- **Language:** TypeScript
- **Build Tool:** Vite
- **UI Library:** Material-UI (MUI) v5
- **HTTP Client:** Axios
- **State Management:** React Query
- **Icons:** Material Icons

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   Copy `.env.example` to `.env` and update if needed:
   ```bash
   cp .env.example .env
   ```

   The default configuration points to `http://localhost:8000/api` for the backend.

## Development

```bash
# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── expenses.ts       # API client for backend communication
│   ├── components/
│   │   ├── FileUploader.tsx  # File upload component with validation
│   │   ├── ExpensePreview.tsx # Preview normalized data table
│   │   └── ImportSummary.tsx  # Import results summary
│   ├── pages/
│   │   └── Dashboard.tsx      # Main dashboard page
│   ├── App.tsx               # App root with theme provider
│   └── main.tsx              # App entry point
├── public/
├── .env.example
└── package.json
```

## Usage Flow

1. **Upload Tab:**
   - Enter the year of expenses
   - Select an Excel file (.xlsx or .xls)
   - Click "Preview" to see normalized data
   - Click "Upload & Import" to save to database

2. **Preview Tab:**
   - View the AI-normalized expense data
   - Check that categories and amounts are correctly detected
   - Review first 10 rows before full import

3. **Summary Tab:**
   - View import statistics
   - See number of records imported and skipped
   - Check for any errors or warnings

## Environment Variables

- `VITE_API_BASE_URL` - Backend API base URL (default: `http://localhost:8000/api`)

## Deployment

### Firebase Hosting

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize project
firebase init hosting

# Build and deploy
npm run build
firebase deploy --only hosting
```

### Other Platforms

The built files in `dist/` can be deployed to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

## Linting

```bash
# Run ESLint
npm run lint
```

## Testing

Tests can be added using Vitest:

```bash
# Install Vitest
npm install -D vitest @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```
