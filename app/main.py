# system
import os
import json
import sys
from typing import Literal
import logging

# server
from fastapi import FastAPI, HTTPException, Request, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

# google cloud
from google.cloud import bigquery
from google.cloud import logging as cloud_logging

# auth flow
from google.auth.transport import requests
from google.oauth2 import id_token

# custom
from google.ads.googleads.client import GoogleAdsClient


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
    async def dispatch(self, request: Request, call_next):
        key = request.headers.get('key', None)

        if key != os.environ.get("ACCESS_KEY"):
            raise HTTPException(status_code=403, detail="ACCESS_DENIED")
        
        response = await call_next(request)
        return response
    
# Middleware to log params
class LogRequestMiddleware(BaseHTTPMiddleware):
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
app.add_middleware(LogRequestMiddleware)


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
@app.get("/home")
def home():
    logger.info("APP: Test request successful.")
    return {"message": "This is a home endpoint"}


@app.get("/protected-data")
async def protected_data(claims: dict = Depends(verify_google_token)):
    
    email = claims.get("email", "anonymous user")
    content = {"message": f"Hello, {email}!"}

    # prints service account email
    logger.info(f"APP: {content}")

    return JSONResponse(content=content)