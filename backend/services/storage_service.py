"""
Google Cloud Storage service for storing uploaded Excel files.
"""
import os
from typing import Optional
from datetime import datetime
from google.cloud import storage


def get_storage_client():
    """Get or create Storage client."""
    try:
        return storage.Client()
    except Exception as e:
        print(f"Warning: Could not initialize Storage client: {str(e)}")
        return None


GCP_BUCKET = os.getenv("GCP_BUCKET", "expense-uploads")


async def upload_file_to_storage(file_path: str, original_filename: str, year: str) -> Optional[str]:
    """
    Upload file to Google Cloud Storage.
    
    Args:
        file_path: Local path to the file
        original_filename: Original name of the uploaded file
        year: Year for organizing files
        
    Returns:
        Public URL of the uploaded file, or None if upload failed
    """
    client = get_storage_client()
    
    if not client:
        print("Storage client not initialized, skipping upload")
        return None
    
    try:
        bucket = client.bucket(GCP_BUCKET)
        
        # Create a unique blob name with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        blob_name = f"uploads/{year}/{timestamp}_{original_filename}"
        
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        
        # Make the blob publicly accessible (optional)
        # blob.make_public()
        
        return f"gs://{GCP_BUCKET}/{blob_name}"
        
    except Exception as e:
        print(f"Error uploading to Cloud Storage: {str(e)}")
        return None


async def download_file_from_storage(blob_name: str, destination_path: str) -> bool:
    """
    Download file from Google Cloud Storage.
    
    Args:
        blob_name: Name of the blob in the bucket
        destination_path: Local path where to save the file
        
    Returns:
        True if successful, False otherwise
    """
    client = get_storage_client()
    
    if not client:
        return False
    
    try:
        bucket = client.bucket(GCP_BUCKET)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_path)
        return True
        
    except Exception as e:
        print(f"Error downloading from Cloud Storage: {str(e)}")
        return False


async def list_files_by_year(year: str) -> list:
    """
    List all uploaded files for a specific year.
    
    Args:
        year: Year to filter by
        
    Returns:
        List of blob names
    """
    client = get_storage_client()
    
    if not client:
        return []
    
    try:
        bucket = client.bucket(GCP_BUCKET)
        blobs = bucket.list_blobs(prefix=f"uploads/{year}/")
        return [blob.name for blob in blobs]
        
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []
