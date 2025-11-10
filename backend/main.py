"""
Main FastAPI application for AI-driven Expense Import System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload_router, expense_router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Expense Import System",
    description="Import and normalize expense data from Excel files using AI",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router.router, prefix="/api", tags=["upload"])
app.include_router(expense_router.router, prefix="/api", tags=["expenses"])


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "AI Expense Import System API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
