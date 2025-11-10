"""
Tests for file utilities.
"""
import pytest
from fastapi import HTTPException, UploadFile
from utils.file_utils import validate_excel_file
from io import BytesIO


def test_validate_excel_file_valid():
    """Test validation of valid Excel files."""
    # Create mock upload file
    file = UploadFile(filename="test.xlsx", file=BytesIO(b"test"))
    
    # Should not raise exception
    validate_excel_file(file)


def test_validate_excel_file_invalid_extension():
    """Test validation rejects invalid file types."""
    file = UploadFile(filename="test.txt", file=BytesIO(b"test"))
    
    with pytest.raises(HTTPException) as exc_info:
        validate_excel_file(file)
    
    assert exc_info.value.status_code == 400
    assert "Invalid file type" in exc_info.value.detail


def test_validate_excel_file_no_filename():
    """Test validation rejects files without filename."""
    file = UploadFile(filename=None, file=BytesIO(b"test"))
    
    with pytest.raises(HTTPException) as exc_info:
        validate_excel_file(file)
    
    assert exc_info.value.status_code == 400
    assert "No filename" in exc_info.value.detail
