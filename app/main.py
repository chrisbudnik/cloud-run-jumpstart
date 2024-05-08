# system
import os
import json
import sys
from typing import Literal
from uuid import uuid4
from datetime import datetime
import logging

# server
from fastapi import FastAPI, HTTPException, Request, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

# google cloud
from google.cloud import bigquery
from google.cloud import storage
from google.cloud import logging as cloud_logging

# auth flow
from google.auth.transport import requests
from google.oauth2 import id_token

# ads
from google.ads.googleads.client import GoogleAdsClient

# custom
from custom_module.bigquery_actions import dataframe_to_bigquery, send_data_to_bigquery 
from custom_module.storage_actions import send_data_to_gcs


app = FastAPI()


# Logging config
client_logging = cloud_logging.Client()
client_logging.setup_logging()
logger = logging.getLogger(__name__)

# set logging destination to stdout (for bigquery logs export)
stream_handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(stream_handler)


# Middleware to verify 'key' in the request headers
class VerifyKeyMiddleware(BaseHTTPMiddleware):
    """
    
    """
    async def dispatch(self, request: Request, call_next):
        key = request.headers.get('access-key', None)

        if key != os.environ.get("ACCESS_KEY"):
            raise HTTPException(status_code=403, detail="ACCESS_DENIED")
        
        response = await call_next(request)
        return response
    
# Middleware to log params
class LogRequestsMiddleware(BaseHTTPMiddleware):
    """
    
    """
    async def dispatch(self, request: Request, call_next):
        # Handle GET requests
        if request.method == "GET":
            params = dict(request.query_params)
            logger.info(f"GET --> {request.url} with params: {params}")

        # Handle POST requests
        if request.method == "POST":
            try:
                body = await request.json()
                logger.info(f"POST --> {request.url} with JSON body: {body}")

            except Exception as e:
                logger.error(f"Error parsing JSON body: {e}")

        # Continue processing the request
        response = await call_next(request)
        return response

# Adding the middleware to the application
app.add_middleware(LogRequestsMiddleware)


def verify_google_token(request: Request):
    """
    OIDC token verification.
    """
    auth_header = request.headers.get("Authorization")

    if auth_header:
        auth_type, creds = auth_header.split(" ", 1)
        
        if auth_type.lower() == "bearer":
            try:
                claims = id_token.verify_oauth2_token(creds, requests.Request())
                return claims
            
            except ValueError as e:
                raise HTTPException(status_code=401, detail=str(e))
            
    raise HTTPException(status_code=401, detail="Invalid or missing token")


# Basic Endpoint - only middleware auth
@app.get("/security/middleware")
def security_middleware():
    """
    
    """
    # Custom logic ...

    content = {"message": "This is an endpoint with middleware auth."}
    logger.info("Test request successful.")
    return JSONResponse(content=content)


@app.get("/security/google-oauth")
async def security_google_oauth(claims: dict = Depends(verify_google_token)):
    """
    
    """
    # Custom logic ...

    # Accessing the email from the claims
    email = claims.get("email", "anonymous user")
    content = {"message": f"This is an endpoint with google auth. Email used: {email}!"}
    logger.info(content)

    return JSONResponse(content=content)


@app.post("/data/to-bigquery")
async def data_to_bigquery(request: Request):
    """
    
    """
    # Set the table reference - can also be defined in config file
    dataset_id = 'your_dataset_id'
    table_id = 'your_table_id'

    # Apply custom logic to process `data`...
    data = await request.json()

    # Connect to BigQuery
    bq_client = bigquery.Client()
    
    # Send data to BigQuery with custom function
    return send_data_to_bigquery(bq_client, dataset_id, table_id, data)


@app.post("/data/to-storage")
async def data_to_storage(request: Request):
    """
    
    """
    # Set the bucket name 
    bucket_name = "your_bucket_name"

    # Create a unique file name: datetime + uuid
    unique_id = str(datetime.now()) + str(uuid4())
    file_name = f"your_file_name_{unique_id}"

    # Unpack data from the request
    data = await request.json()

    # Connect to GCS
    storage_client = storage.Client()
    
    # Send data to GCS using the helper function
    return send_data_to_gcs(storage_client, bucket_name, file_name, data)


@app.post("/pubsub/to-bigquery")
def pubsub_to_bigquery():
    """
    
    """
    pass


@app.post("/eventarc/gcs-to-bigquery")
def eventarc_gcs_to_bigquery():
    """
    
    """
    pass


@app.post("/database/mysql-to-bigquery")
def database_msql_to_bigquery():
    """
    
    """
    pass

