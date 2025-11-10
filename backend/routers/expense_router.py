"""
Expense router for querying and managing expense data.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from services.firestore_service import (
    get_expenses_by_year,
    get_all_years,
    delete_expenses_by_year
)


router = APIRouter()


@router.get("/expenses/{year}")
async def get_expenses(
    year: str,
    limit: int = Query(default=100, ge=1, le=1000)
) -> Dict[str, Any]:
    """
    Get expenses for a specific year.
    
    Args:
        year: Year to query (e.g., "2023")
        limit: Maximum number of records to return
        
    Returns:
        Dictionary with expense data
    """
    try:
        expenses = await get_expenses_by_year(year, limit)
        
        return {
            "status": "ok",
            "year": year,
            "count": len(expenses),
            "expenses": expenses
        }
        
    except Exception as e:
        print(f"Error retrieving expenses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses")


@router.get("/expenses")
async def list_all_years() -> Dict[str, Any]:
    """
    Get all years that have expense data.
    
    Returns:
        Dictionary with list of years
    """
    try:
        years = await get_all_years()
        
        return {
            "status": "ok",
            "years": years,
            "count": len(years)
        }
        
    except Exception as e:
        print(f"Error retrieving years: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve years")


@router.delete("/expenses/{year}")
async def delete_year_expenses(year: str) -> Dict[str, Any]:
    """
    Delete all expenses for a specific year.
    
    Args:
        year: Year to delete
        
    Returns:
        Dictionary with deletion results
    """
    try:
        result = await delete_expenses_by_year(year)
        
        if result["status"] == "error":
            # Log the error message internally
            print(f"Deletion error: {result.get('message', 'Unknown error')}")
            raise HTTPException(status_code=500, detail="Failed to delete expenses")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error internally but don't expose details to user
        print(f"Error deleting expenses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete expenses")


@router.get("/stats/{year}")
async def get_year_stats(year: str) -> Dict[str, Any]:
    """
    Get statistics for a specific year's expenses.
    
    Args:
        year: Year to analyze
        
    Returns:
        Dictionary with expense statistics
    """
    try:
        expenses = await get_expenses_by_year(year, limit=1000)
        
        if not expenses:
            return {
                "status": "ok",
                "year": year,
                "total_expenses": 0,
                "total_amount": 0,
                "categories": {}
            }
        
        # Calculate statistics
        total_amount = sum(exp.get("amount", 0) for exp in expenses)
        categories = {}
        
        for exp in expenses:
            category = exp.get("category", "Unknown")
            if category not in categories:
                categories[category] = {
                    "count": 0,
                    "total": 0
                }
            categories[category]["count"] += 1
            categories[category]["total"] += exp.get("amount", 0)
        
        return {
            "status": "ok",
            "year": year,
            "total_expenses": len(expenses),
            "total_amount": total_amount,
            "categories": categories
        }
        
    except Exception as e:
        print(f"Error calculating stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate statistics")
