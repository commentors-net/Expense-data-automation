"""
AI Parser service for normalizing expense data using Gemini API.
"""
import os
import json
from typing import List, Dict, Any
import httpx
from datetime import datetime


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"


async def normalize_expense_data(raw_data: List[Dict[str, Any]], year: str) -> List[Dict[str, Any]]:
    """
    Normalize expense data using Gemini API.
    
    Args:
        raw_data: List of dictionaries from Excel rows
        year: The year of the expense data
        
    Returns:
        List of normalized expense dictionaries with format:
        {
            "date": "YYYY-MM-DD",
            "category": "Category name",
            "description": "Description text",
            "amount": float
        }
    """
    if not GEMINI_API_KEY:
        # Fallback to mock normalization if API key is not set
        return _mock_normalize_expense_data(raw_data, year)
    
    try:
        # Prepare the prompt for Gemini
        prompt = f"""
You are an expert data normalizer for expense records.

Given the following array of expense rows from an Excel sheet for year {year}, 
analyze the data and normalize it to a consistent JSON format.

Input data (sample):
{json.dumps(raw_data[:5], indent=2)}

Your task:
1. Identify which columns represent date, category/type, description, and amount
2. Convert all dates to "YYYY-MM-DD" format (use year {year} if year is missing)
3. Ensure amounts are numeric (float)
4. Assign appropriate expense categories (e.g., Transport, Food, Office, Utilities, etc.)
5. Preserve or clean description text

Return ONLY a valid JSON array with this exact format for ALL rows:
[
  {{
    "date": "YYYY-MM-DD",
    "category": "Category",
    "description": "Description text",
    "amount": 0.00
  }}
]

Important:
- Output ONLY valid JSON, no explanations or markdown
- Process all {len(raw_data)} rows from the input
- If a field is unclear, make a reasonable inference
- Amounts must be positive numbers
"""

        # Call Gemini API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.2,
                        "topK": 40,
                        "topP": 0.95,
                    }
                }
            )
            
            if response.status_code != 200:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                return _mock_normalize_expense_data(raw_data, year)
            
            result = response.json()
            
            # Extract the generated text
            if "candidates" in result and len(result["candidates"]) > 0:
                generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Clean the response - remove markdown code blocks if present
                generated_text = generated_text.strip()
                if generated_text.startswith("```json"):
                    generated_text = generated_text[7:]
                if generated_text.startswith("```"):
                    generated_text = generated_text[3:]
                if generated_text.endswith("```"):
                    generated_text = generated_text[:-3]
                generated_text = generated_text.strip()
                
                # Parse JSON response
                normalized_data = json.loads(generated_text)
                
                # Validate the structure
                for item in normalized_data:
                    if not all(key in item for key in ["date", "category", "description", "amount"]):
                        raise ValueError("Invalid normalized data structure")
                
                return normalized_data
            else:
                print("No candidates in Gemini response")
                return _mock_normalize_expense_data(raw_data, year)
                
    except Exception as e:
        print(f"Error in AI normalization: {str(e)}")
        # Fallback to mock normalization
        return _mock_normalize_expense_data(raw_data, year)


def _mock_normalize_expense_data(raw_data: List[Dict[str, Any]], year: str) -> List[Dict[str, Any]]:
    """
    Mock normalization function for development/testing without API key.
    
    Args:
        raw_data: List of dictionaries from Excel rows
        year: The year of the expense data
        
    Returns:
        List of normalized expense dictionaries
    """
    normalized = []
    
    for row in raw_data:
        # Try to find date, amount, and description fields
        date_val = None
        amount_val = 0.0
        description_val = "Expense"
        category_val = "General"
        
        for key, value in row.items():
            key_lower = str(key).lower()
            
            # Try to identify date
            if 'date' in key_lower or 'day' in key_lower or 'time' in key_lower:
                try:
                    if isinstance(value, str):
                        # Try parsing date
                        date_val = value
                    elif hasattr(value, 'date'):
                        date_val = value.strftime('%Y-%m-%d')
                except:
                    pass
            
            # Try to identify amount
            if 'amount' in key_lower or 'price' in key_lower or 'cost' in key_lower or 'rm' in key_lower or key_lower in ['amount', 'total']:
                try:
                    amount_val = float(str(value).replace(',', '').replace('$', '').replace('RM', '').strip())
                except:
                    pass
            
            # Try to identify description
            if 'description' in key_lower or 'detail' in key_lower or 'item' in key_lower or 'particular' in key_lower:
                description_val = str(value)
            
            # Try to identify category
            if 'category' in key_lower or 'type' in key_lower or 'class' in key_lower:
                category_val = str(value)
        
        # If no date found, use first day of the year
        if not date_val:
            date_val = f"{year}-01-01"
        elif not date_val.startswith(year):
            # Try to add year if missing
            if '/' in date_val or '-' in date_val:
                date_val = f"{year}-{date_val}"
        
        normalized.append({
            "date": date_val,
            "category": category_val,
            "description": description_val,
            "amount": amount_val
        })
    
    return normalized
