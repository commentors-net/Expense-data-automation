"""
SQLite Database Service - Local development database.

Implements the same interface as Firestore for seamless switching.
"""
import os
import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class SQLiteDatabase:
    """SQLite implementation for local development."""
    
    def __init__(self, db_path: str = "expenses.db"):
        """Initialize SQLite database."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT,
                description TEXT,
                amount REAL NOT NULL,
                source_file TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                raw_data TEXT
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_year ON expenses(year)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_date ON expenses(date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON expenses(category)
        """)
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    async def save_expenses(
        self, 
        year: str, 
        expense_data: List[Dict[str, Any]], 
        source_file: str
    ) -> Dict[str, Any]:
        """
        Save normalized expense data to SQLite.
        
        Args:
            year: The year of the expenses
            expense_data: List of normalized expense dictionaries
            source_file: Original filename
            
        Returns:
            Dictionary with import statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        try:
            for expense in expense_data:
                try:
                    cursor.execute("""
                        INSERT INTO expenses 
                        (year, date, category, description, amount, source_file, imported_at, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        year,
                        expense.get("date"),
                        expense.get("category"),
                        expense.get("description"),
                        expense.get("amount"),
                        source_file,
                        datetime.utcnow().isoformat(),
                        json.dumps(expense)
                    ))
                    imported_count += 1
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"Error saving expense: {str(e)}")
            
            conn.commit()
            
            return {
                "imported": imported_count,
                "skipped": skipped_count,
                "status": "ok" if imported_count > 0 else "error",
                "errors": errors[:10]
            }
            
        except Exception as e:
            conn.rollback()
            return {
                "imported": imported_count,
                "skipped": len(expense_data) - imported_count,
                "status": "error",
                "message": str(e)
            }
        finally:
            conn.close()
    
    async def get_expenses_by_year(
        self, 
        year: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all expenses for a specific year."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, year, date, category, description, amount, 
                   source_file, imported_at
            FROM expenses
            WHERE year = ?
            ORDER BY date DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (year,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "year": row[1],
                "date": row[2],
                "category": row[3],
                "description": row[4],
                "amount": row[5],
                "source_file": row[6],
                "imported_at": row[7]
            }
            for row in rows
        ]
    
    async def get_all_years(self) -> List[str]:
        """Get list of all years that have expense data."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT year
            FROM expenses
            ORDER BY year DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    async def get_year_statistics(self, year: str) -> Dict[str, Any]:
        """Get statistics for a specific year."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total expenses and amount
        cursor.execute("""
            SELECT COUNT(*), SUM(amount)
            FROM expenses
            WHERE year = ?
        """, (year,))
        
        count, total = cursor.fetchone()
        
        # Category breakdown
        cursor.execute("""
            SELECT category, COUNT(*), SUM(amount)
            FROM expenses
            WHERE year = ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """, (year,))
        
        categories = [
            {
                "category": row[0] or "Uncategorized",
                "count": row[1],
                "total": row[2]
            }
            for row in cursor.fetchall()
        ]
        
        # Monthly breakdown
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, COUNT(*), SUM(amount)
            FROM expenses
            WHERE year = ?
            GROUP BY month
            ORDER BY month
        """, (year,))
        
        months = [
            {
                "month": row[0],
                "count": row[1],
                "total": row[2]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "year": year,
            "total_expenses": count or 0,
            "total_amount": total or 0.0,
            "by_category": categories,
            "by_month": months
        }
    
    async def delete_expenses_by_year(self, year: str) -> Dict[str, Any]:
        """Delete all expenses for a specific year."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get count before deletion
            cursor.execute("SELECT COUNT(*) FROM expenses WHERE year = ?", (year,))
            count = cursor.fetchone()[0]
            
            # Delete
            cursor.execute("DELETE FROM expenses WHERE year = ?", (year,))
            conn.commit()
            
            return {
                "status": "ok",
                "deleted": count,
                "message": f"Deleted {count} expenses from {year}"
            }
            
        except Exception as e:
            conn.rollback()
            return {
                "status": "error",
                "deleted": 0,
                "message": str(e)
            }
        finally:
            conn.close()
    
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
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, year, date, category, description, amount, 
                   source_file, imported_at
            FROM expenses
            WHERE 1=1
        """
        params = []
        
        if year:
            query += " AND year = ?"
            params.append(year)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
        
        if min_amount is not None:
            query += " AND amount >= ?"
            params.append(min_amount)
        
        if max_amount is not None:
            query += " AND amount <= ?"
            params.append(max_amount)
        
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "year": row[1],
                "date": row[2],
                "category": row[3],
                "description": row[4],
                "amount": row[5],
                "source_file": row[6],
                "imported_at": row[7]
            }
            for row in rows
        ]
