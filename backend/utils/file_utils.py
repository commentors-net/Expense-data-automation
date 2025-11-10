"""
File utility functions for handling Excel file uploads and validation.
"""
import os
import tempfile
from typing import Tuple
from fastapi import UploadFile, HTTPException


ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_excel_file(file: UploadFile) -> None:
    """
    Validate uploaded Excel file.
    
    Args:
        file: The uploaded file
        
    Raises:
        HTTPException: If file validation fails
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )


async def save_upload_file_temp(upload_file: UploadFile) -> Tuple[str, str]:
    """
    Save uploaded file to temporary location.
    
    Args:
        upload_file: The file to save
        
    Returns:
        Tuple of (temp_file_path, original_filename)
    """
    try:
        # Create temporary file
        suffix = os.path.splitext(upload_file.filename)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        # Write uploaded file content to temp file
        content = await upload_file.read()
        temp_file.write(content)
        temp_file.close()
        
        return temp_file.name, upload_file.filename
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


def cleanup_temp_file(file_path: str) -> None:
    """
    Remove temporary file safely.
    
    Args:
        file_path: Path to the temporary file
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Warning: Failed to cleanup temp file {file_path}: {str(e)}")
