"""
Tests for AI parser service.
"""
import pytest
from services.ai_parser import _mock_normalize_expense_data


def test_mock_normalize_expense_data():
    """Test mock normalization of expense data."""
    # Sample raw data
    raw_data = [
        {"Date": "Jan 5", "Description": "Office supplies", "Amount": "120.50"},
        {"Date": "Jan 6", "Details": "Taxi fare", "Cost": 35.00},
        {"Spending": "Jan 7", "Item": "Lunch", "RM": "25.50"}
    ]
    
    # Normalize
    result = _mock_normalize_expense_data(raw_data, "2023")
    
    # Assertions
    assert len(result) == 3
    assert all("date" in item for item in result)
    assert all("category" in item for item in result)
    assert all("description" in item for item in result)
    assert all("amount" in item for item in result)
    
    # Check first item
    assert result[0]["amount"] == 120.50
    assert result[0]["description"] == "Office supplies"


def test_mock_normalize_handles_missing_fields():
    """Test that mock normalization handles missing fields gracefully."""
    raw_data = [
        {"Unknown": "Some value"},
    ]
    
    result = _mock_normalize_expense_data(raw_data, "2023")
    
    assert len(result) == 1
    assert result[0]["date"] == "2023-01-01"  # Default date
    assert result[0]["amount"] == 0.0  # Default amount
    assert result[0]["category"] == "General"
    assert result[0]["description"] == "Expense"


@pytest.mark.asyncio
async def test_normalize_expense_data_without_api_key():
    """Test that normalization falls back to mock when API key is not set."""
    from services.ai_parser import normalize_expense_data
    
    raw_data = [
        {"Date": "2023-01-10", "Description": "Test expense", "Amount": 50.00}
    ]
    
    # This should use mock normalization since API key is likely not set in tests
    result = await normalize_expense_data(raw_data, "2023")
    
    assert len(result) > 0
    assert isinstance(result, list)
