"""
Expense router for querying and managing expense data.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from db_factory import db


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
        expenses = await db.get_expenses_by_year(year, limit)
        
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
        years = await db.get_all_years()
        
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
        result = await db.delete_expenses_by_year(year)
        
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
        stats = await db.get_year_statistics(year)
        
        return {
            "status": "ok",
            **stats
        }
        
    except Exception as e:
        print(f"Error calculating stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate statistics")


@router.get("/search")
async def search_expenses(
    year: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None)
) -> Dict[str, Any]:
    """
    Search expenses with various filters.
    
    Args:
        year: Filter by year
        category: Filter by category
        date_from: Filter by start date (YYYY-MM-DD)
        date_to: Filter by end date (YYYY-MM-DD)
        min_amount: Minimum amount
        max_amount: Maximum amount
        
    Returns:
        Dictionary with filtered expense data
    """
    try:
        expenses = await db.search_expenses(
            year=year,
            category=category,
            date_from=date_from,
            date_to=date_to,
            min_amount=min_amount,
            max_amount=max_amount
        )
        
        return {
            "status": "ok",
            "count": len(expenses),
            "expenses": expenses
        }
        
    except Exception as e:
        print(f"Error searching expenses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search expenses")
