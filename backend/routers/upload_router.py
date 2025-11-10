"""
Upload router for handling Excel file uploads and processing.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any
import pandas as pd
from utils.file_utils import validate_excel_file, save_upload_file_temp, cleanup_temp_file
from services.ai_parser import normalize_expense_data
from services.storage_service import upload_file_to_storage
from db_factory import db


router = APIRouter()


@router.post("/upload")
async def upload_expense_file(
    file: UploadFile = File(...),
    year: str = Form(...)
) -> Dict[str, Any]:
    """
    Upload and process an Excel file containing expense data.
    
    Args:
        file: Excel file upload
        year: Year of the expenses (e.g., "2023")
        
    Returns:
        Dictionary with processing results including:
        - imported: number of records imported
        - skipped: number of records skipped
        - status: "ok" or "error"
    """
    temp_file_path = None
    
    try:
        # Validate file
        validate_excel_file(file)
        
        # Validate year
        if not year.isdigit() or len(year) != 4:
            raise HTTPException(status_code=400, detail="Year must be a 4-digit number")
        
        # Save file temporarily
        temp_file_path, original_filename = await save_upload_file_temp(file)
        
        # Parse Excel file
        try:
            df = pd.read_excel(temp_file_path, engine='openpyxl')
            
            # Convert DataFrame to list of dictionaries
            raw_data = df.to_dict(orient='records')
            
            if not raw_data:
                raise HTTPException(status_code=400, detail="Excel file is empty")
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Excel parsing error: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to parse Excel file. Please ensure it is a valid Excel file.")
        
        # Normalize data using AI
        try:
            normalized_data = await normalize_expense_data(raw_data, year)
            
            if not normalized_data:
                raise HTTPException(status_code=500, detail="AI normalization returned no data")
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"AI normalization error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to normalize data")
        
        # Save to database (SQLite or Firestore)
        try:
            result = await db.save_expenses(year, normalized_data, original_filename)
        except Exception as e:
            print(f"Database save error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save expenses to database")
        
        # Upload to Cloud Storage (optional, doesn't fail the request)
        try:
            storage_url = await upload_file_to_storage(temp_file_path, original_filename, year)
            if storage_url:
                result['storage_url'] = storage_url
        except Exception as e:
            print(f"Warning: Cloud Storage upload failed: {str(e)}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error internally but don't expose details to user
        print(f"Unexpected error in upload: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during upload")
    finally:
        # Cleanup temporary file
        if temp_file_path:
            cleanup_temp_file(temp_file_path)


@router.post("/preview")
async def preview_expense_file(
    file: UploadFile = File(...),
    year: str = Form(...)
) -> Dict[str, Any]:
    """
    Preview normalized data without saving to database.
    
    Args:
        file: Excel file upload
        year: Year of the expenses
        
    Returns:
        Dictionary with normalized expense data preview
    """
    temp_file_path = None
    
    try:
        # Validate file
        validate_excel_file(file)
        
        # Validate year
        if not year.isdigit() or len(year) != 4:
            raise HTTPException(status_code=400, detail="Year must be a 4-digit number")
        
        # Save file temporarily
        temp_file_path, original_filename = await save_upload_file_temp(file)
        
        # Parse Excel file
        try:
            df = pd.read_excel(temp_file_path, engine='openpyxl')
            raw_data = df.to_dict(orient='records')
            
            if not raw_data:
                raise HTTPException(status_code=400, detail="Excel file is empty")
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Excel parsing error in preview: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to parse Excel file. Please ensure it is a valid Excel file.")
        
        # Normalize data using AI
        try:
            # Limit preview to first 10 rows for faster response
            preview_data = raw_data[:10]
            normalized_data = await normalize_expense_data(preview_data, year)
            
            return {
                "status": "ok",
                "total_rows": len(raw_data),
                "preview_rows": len(normalized_data),
                "data": normalized_data,
                "filename": original_filename
            }
            
        except Exception as e:
            print(f"AI normalization error in preview: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to normalize data")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in preview: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during preview")
    finally:
        # Cleanup temporary file
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
