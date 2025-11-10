"""
Firestore Database Service - Production database.

Implements the same interface as SQLite for seamless switching.
Renamed from firestore_service.py to firestore_db.py for consistency.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


class FirestoreDatabase:
    """Firestore implementation for production environment."""
    
    def __init__(self):
        """Initialize Firestore client."""
        self.collection_name = os.getenv("FIRESTORE_COLLECTION", "expenses")
        self.db = self._get_firestore_client()
    
    def _get_firestore_client(self):
        """Get or create Firestore client."""
        try:
            return firestore.Client()
        except Exception as e:
            print(f"Warning: Could not initialize Firestore client: {str(e)}")
            return None


    async def save_expenses(
        self, 
        year: str, 
        expense_data: List[Dict[str, Any]], 
        source_file: str
    ) -> Dict[str, Any]:
        """
        Save normalized expense data to Firestore.
        
        Args:
            year: The year of the expenses
            expense_data: List of normalized expense dictionaries
            source_file: Original filename
            
        Returns:
            Dictionary with import statistics
        """
        if not self.db:
            return {
                "imported": 0,
                "skipped": len(expense_data),
                "status": "error",
                "message": "Firestore client not initialized"
            }
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        # Use batch writes for efficiency
        batch = self.db.batch()
        batch_size = 0
        max_batch_size = 500  # Firestore limit
        
        try:
            for expense in expense_data:
                try:
                    # Add metadata
                    expense_with_meta = {
                        **expense,
                        "year": year,
                        "source_file": source_file,
                        "imported_at": datetime.utcnow().isoformat()
                    }
                    
                    # Create document reference in year subcollection
                    doc_ref = self.db.collection(self.collection_name).document(year).collection("records").document()
                    batch.set(doc_ref, expense_with_meta)
                    
                    batch_size += 1
                    imported_count += 1
                    
                    # Commit batch if it reaches the limit
                    if batch_size >= max_batch_size:
                        batch.commit()
                        batch = self.db.batch()
                        batch_size = 0
                        
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"Error processing expense: {str(e)}")
            
            # Commit remaining items
            if batch_size > 0:
                batch.commit()
            
            return {
                "imported": imported_count,
                "skipped": skipped_count,
                "status": "ok" if imported_count > 0 else "error",
                "errors": errors[:10]  # Limit error messages
            }
            
        except Exception as e:
            return {
                "imported": imported_count,
                "skipped": len(expense_data) - imported_count,
                "status": "error",
                "message": str(e)
            }

    async def get_expenses_by_year(
        self, 
        year: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all expenses for a specific year."""
        if not self.db:
            return []
        
        try:
            expenses_ref = self.db.collection(self.collection_name).document(year).collection("records")
            
            if limit:
                docs = expenses_ref.limit(limit).stream()
            else:
                docs = expenses_ref.stream()
            
            expenses = []
            for doc in docs:
                expense = doc.to_dict()
                expense['id'] = doc.id
                expenses.append(expense)
            
            return expenses
            
        except Exception as e:
            print(f"Error retrieving expenses: {str(e)}")
            return []
    
    async def get_all_years(self) -> List[str]:
        """Get list of all years that have expense data."""
        if not self.db:
            return []
        
        try:
            years_ref = self.db.collection(self.collection_name).list_documents()
            years = [doc.id for doc in years_ref]
            return sorted(years, reverse=True)
            
        except Exception as e:
            print(f"Error retrieving years: {str(e)}")
            return []
    
    async def get_year_statistics(self, year: str) -> Dict[str, Any]:
        """Get statistics for a specific year."""
        if not self.db:
            return {
                "year": year,
                "total_expenses": 0,
                "total_amount": 0.0,
                "by_category": [],
                "by_month": []
            }
        
        try:
            expenses_ref = self.db.collection(self.collection_name).document(year).collection("records")
            docs = expenses_ref.stream()
            
            expenses = [doc.to_dict() for doc in docs]
            
            # Calculate statistics
            total_amount = sum(exp.get("amount", 0) for exp in expenses)
            
            # Category breakdown
            category_stats = {}
            for exp in expenses:
                cat = exp.get("category") or "Uncategorized"
                if cat not in category_stats:
                    category_stats[cat] = {"count": 0, "total": 0}
                category_stats[cat]["count"] += 1
                category_stats[cat]["total"] += exp.get("amount", 0)
            
            by_category = [
                {"category": cat, **stats}
                for cat, stats in sorted(
                    category_stats.items(),
                    key=lambda x: x[1]["total"],
                    reverse=True
                )
            ]
            
            # Monthly breakdown
            month_stats = {}
            for exp in expenses:
                date_str = exp.get("date", "")
                if date_str:
                    month = date_str[:7]  # YYYY-MM
                    if month not in month_stats:
                        month_stats[month] = {"count": 0, "total": 0}
                    month_stats[month]["count"] += 1
                    month_stats[month]["total"] += exp.get("amount", 0)
            
            by_month = [
                {"month": month, **stats}
                for month, stats in sorted(month_stats.items())
            ]
            
            return {
                "year": year,
                "total_expenses": len(expenses),
                "total_amount": total_amount,
                "by_category": by_category,
                "by_month": by_month
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {str(e)}")
            return {
                "year": year,
                "total_expenses": 0,
                "total_amount": 0.0,
                "by_category": [],
                "by_month": []
            }
    
    async def delete_expenses_by_year(self, year: str) -> Dict[str, Any]:
        """Delete all expenses for a specific year."""
        if not self.db:
            return {
                "status": "error",
                "deleted": 0,
                "message": "Firestore client not initialized"
            }
        
        try:
            expenses_ref = self.db.collection(self.collection_name).document(year).collection("records")
            
            # Delete in batches
            deleted = 0
            batch = self.db.batch()
            docs = expenses_ref.limit(500).stream()
            
            for doc in docs:
                batch.delete(doc.reference)
                deleted += 1
            
            batch.commit()
            
            # Delete the year document itself
            self.db.collection(self.collection_name).document(year).delete()
            
            return {
                "status": "ok",
                "deleted": deleted,
                "message": f"Deleted {deleted} expenses from {year}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "deleted": 0,
                "message": str(e)
            }
    
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
        if not self.db:
            return []
        
        try:
            # Start with all expenses
            if year:
                expenses_ref = self.db.collection(self.collection_name).document(year).collection("records")
                docs = expenses_ref.stream()
            else:
                # Query all years
                all_expenses = []
                years_ref = self.db.collection(self.collection_name).list_documents()
                for year_doc in years_ref:
                    records_ref = year_doc.collection("records")
                    all_expenses.extend([doc.to_dict() | {"id": doc.id} for doc in records_ref.stream()])
                docs = all_expenses
            
            # Convert to list if needed
            if not isinstance(docs, list):
                expenses = [doc.to_dict() | {"id": doc.id} for doc in docs]
            else:
                expenses = docs
            
            # Apply filters
            filtered = expenses
            
            if category:
                filtered = [e for e in filtered if e.get("category") == category]
            
            if date_from:
                filtered = [e for e in filtered if e.get("date", "") >= date_from]
            
            if date_to:
                filtered = [e for e in filtered if e.get("date", "") <= date_to]
            
            if min_amount is not None:
                filtered = [e for e in filtered if e.get("amount", 0) >= min_amount]
            
            if max_amount is not None:
                filtered = [e for e in filtered if e.get("amount", 0) <= max_amount]
            
            return sorted(filtered, key=lambda x: x.get("date", ""), reverse=True)
            
        except Exception as e:
            print(f"Error searching expenses: {str(e)}")
            return []
