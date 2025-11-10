"""
Database Factory - Automatically selects database based on environment.

- ENVIRONMENT=development → SQLite (local file)
- ENVIRONMENT=production → Firestore (Google Cloud)
"""
import os
from typing import Protocol, List, Dict, Any, Optional
from datetime import datetime


class DatabaseInterface(Protocol):
    """
    Common interface that both SQLite and Firestore must implement.
    All database operations for expense management.
    """
    
    async def save_expenses(
        self, 
        year: str, 
        expense_data: List[Dict[str, Any]], 
        source_file: str
    ) -> Dict[str, Any]:
        """Save normalized expense data to database."""
        ...
    
    async def get_expenses_by_year(
        self, 
        year: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all expenses for a specific year."""
        ...
    
    async def get_all_years(self) -> List[str]:
        """Get list of all years that have expense data."""
        ...
    
    async def get_year_statistics(self, year: str) -> Dict[str, Any]:
        """Get statistics for a specific year."""
        ...
    
    async def delete_expenses_by_year(self, year: str) -> Dict[str, Any]:
        """Delete all expenses for a specific year."""
        ...
    
    async def search_expenses(
        self,
        year: Optional[str] = None,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search expenses with various filters."""
        ...


def get_database() -> DatabaseInterface:
    """
    Factory function to get the appropriate database instance.
    
    Returns:
        Database instance (SQLite or Firestore) based on ENVIRONMENT variable
    """
    environment = os.getenv("ENVIRONMENT", "production").lower()
    
    if environment == "development":
        from services.sqlite_db import SQLiteDatabase
        print("🔧 Using SQLite database (development mode)")
        return SQLiteDatabase()
    else:
        from services.firestore_db import FirestoreDatabase
        print("☁️ Using Firestore database (production mode)")
        return FirestoreDatabase()


# Global database instance
db = get_database()
