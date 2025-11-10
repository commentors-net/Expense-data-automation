"""
Firestore service for storing and retrieving expense data.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


# Initialize Firestore client
def get_firestore_client():
    """Get or create Firestore client."""
    try:
        return firestore.Client()
    except Exception as e:
        print(f"Warning: Could not initialize Firestore client: {str(e)}")
        return None


FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "expenses")


async def save_expenses(year: str, expense_data: List[Dict[str, Any]], source_file: str) -> Dict[str, Any]:
    """
    Save normalized expense data to Firestore.
    
    Args:
        year: The year of the expenses
        expense_data: List of normalized expense dictionaries
        source_file: Original filename
        
    Returns:
        Dictionary with import statistics
    """
    db = get_firestore_client()
    
    if not db:
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
    batch = db.batch()
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
                doc_ref = db.collection(FIRESTORE_COLLECTION).document(year).collection("records").document()
                batch.set(doc_ref, expense_with_meta)
                
                batch_size += 1
                imported_count += 1
                
                # Commit batch if it reaches the limit
                if batch_size >= max_batch_size:
                    batch.commit()
                    batch = db.batch()
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


async def get_expenses_by_year(year: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieve expenses for a specific year.
    
    Args:
        year: The year to query
        limit: Maximum number of records to return
        
    Returns:
        List of expense records
    """
    db = get_firestore_client()
    
    if not db:
        return []
    
    try:
        expenses_ref = db.collection(FIRESTORE_COLLECTION).document(year).collection("records")
        docs = expenses_ref.limit(limit).stream()
        
        expenses = []
        for doc in docs:
            expense = doc.to_dict()
            expense['id'] = doc.id
            expenses.append(expense)
        
        return expenses
        
    except Exception as e:
        print(f"Error retrieving expenses: {str(e)}")
        return []


async def get_all_years() -> List[str]:
    """
    Get all years that have expense data.
    
    Returns:
        List of year strings
    """
    db = get_firestore_client()
    
    if not db:
        return []
    
    try:
        years_ref = db.collection(FIRESTORE_COLLECTION).list_documents()
        years = [doc.id for doc in years_ref]
        return sorted(years, reverse=True)
        
    except Exception as e:
        print(f"Error retrieving years: {str(e)}")
        return []


async def delete_expenses_by_year(year: str) -> Dict[str, Any]:
    """
    Delete all expenses for a specific year.
    
    Args:
        year: The year to delete
        
    Returns:
        Dictionary with deletion statistics
    """
    db = get_firestore_client()
    
    if not db:
        return {
            "deleted": 0,
            "status": "error",
            "message": "Firestore client not initialized"
        }
    
    try:
        expenses_ref = db.collection(FIRESTORE_COLLECTION).document(year).collection("records")
        
        # Delete in batches
        deleted = 0
        batch = db.batch()
        docs = expenses_ref.limit(500).stream()
        
        for doc in docs:
            batch.delete(doc.reference)
            deleted += 1
        
        batch.commit()
        
        # Delete the year document itself
        db.collection(FIRESTORE_COLLECTION).document(year).delete()
        
        return {
            "deleted": deleted,
            "status": "ok"
        }
        
    except Exception as e:
        return {
            "deleted": 0,
            "status": "error",
            "message": str(e)
        }
