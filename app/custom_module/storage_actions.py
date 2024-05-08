from google.cloud import storage
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import logging

# Set up logging
logger = logging.getLogger(__name__)


def send_data_to_gcs(
        client: storage.Client, 
        bucket_name: str, 
        file_name: str, 
        data: bytes
    ) -> JSONResponse:
    """
    
    """
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(data)
        logger.info(f"Data successfully uploaded to {file_name} in bucket {bucket_name}.")
        return JSONResponse({"message": "Data successfully uploaded to Cloud Storage."}, status_code=200)
    
    except Exception as e:
        logger.error(f"Failed to upload data to Cloud Storage: {e}")
        raise HTTPException(status_code=500, detail="Failed to send data to Cloud Storage.")