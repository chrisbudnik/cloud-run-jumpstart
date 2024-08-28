# system
from typing import Literal, Optional, List
from datetime import datetime
import logging
from pydantic import BaseModel
import pandas as pd

# server
from fastapi import FastAPI, HTTPException, Request, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

# google
from google.cloud import logging as cloud_logging
from google.auth.transport import requests
from google.oauth2 import id_token
from google.cloud import bigquery
from google.cloud import storage


app = FastAPI()

# Logging config
client_logging = cloud_logging.Client()
client_logging.setup_logging()
logger = logging.getLogger(__name__)


def verify_google_token(request: Request):
    """OIDC token verification."""

    auth_header = request.headers.get("Authorization")
    if auth_header:
        auth_type, creds = auth_header.split(" ", 1)
        if auth_type.lower() == "bearer":
            try:
                claims = id_token.verify_oauth2_token(creds, requests.Request())
                return claims
            except ValueError as e:
                raise HTTPException(status_code=401, detail="Invalid or missing token")
    raise HTTPException(status_code=401, detail="Invalid or missing token")


class VerifyGoogleTokenMiddleware(BaseHTTPMiddleware):
    """Authenticate each requests with Google OIDC tokens."""

    async def dispatch(self, request: Request, call_next):
        try:
            claims = verify_google_token(request)
            request.state.claims = claims
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        
        response = await call_next(request)
        return response
    
app.add_middleware(VerifyGoogleTokenMiddleware)

class ResponseSchema(BaseModel):
    "Response schema for service endpoints."
    status_code: int
    detail: str

class ExampleDataSchema(BaseModel):
    "Example marketing campaign data schema. Used to demonstrate data processing."

    date: str
    campaign: str
    clicks: int
    impressions: int
    cost: float

class BigQueryExportConfig(BaseModel):
    "BigQuery export configuration, can be extended to accommodate more options."

    table_id: str
    partition_field: Optional[str] = None
    clustering_fields: Optional[List[str]] = None
    write_disposition: Optional[Literal["WRITE_TRUNCATE", "WRITE_APPEND", "WRITE_EMPTY"]] = "WRITE_APPEND"  


def validate_bigquery_config(config: BigQueryExportConfig):
    """Example function to validate input parameters."""
    pass 


@app.get("/tests/server-time")
def test_endpoint():
    """Edpoint to test the middleware. Returns the server time."""

    content = {"message": f"Authenticated request. Server time: {datetime.now()}"}
    logger.info("Testing endpoint success.")
    return ResponseSchema(status_code=200, detail=content)



@app.post("/upload/bigquery")
async def upload_to_bigquery(
    data: ExampleDataSchema, 
    config: BigQueryExportConfig = Depends(validate_bigquery_config)) -> ResponseSchema:
    """Upload data example campaign data to BigQuery table. Request is validated by pydantic models. 
    Before export date is chacked against bigquery schema."""

    table_ref = bigquery.TableReference.from_string(config.table_id)
    schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("campaign", "STRING"),
        bigquery.SchemaField("clicks", "INT64"),
        bigquery.SchemaField("impressions", "INT64"),
        bigquery.SchemaField("cost", "FLOAT64"),
    ]

    try:
        # Convert: pydantic -> dict -> DataFrame
        df = pd.DataFrame([item.dict() for item in data])
        df['date'] = pd.to_datetime(df['date'])

        job_config = bigquery.LoadJobConfig(
            schema = schema,
            write_disposition = config.write_disposition,
            clustering_fields= config.clustering_fields,
            time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=config.partition_field
            )
        )
        client = bigquery.Client()
        job = client.load_table_from_dataframe(data, table_ref, job_config=job_config)
        job.result()

    except Exception as e:
        logger.error(f"Failed to upload data to BigQuery. {e}")
        raise HTTPException(status_code=500, detail="Failed to upload data to BigQuery.")

    return ResponseSchema(status_code=200, detail="Data uploaded to BigQuery successfully.")


@app.post("/data/to-storage")
async def data_to_storage(request: Request):
    """
    
    """
    pass


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


@app.post("/database/bigquery-to-mysql")
def database_msql_to_bigquery():
    """
    
    """
    pass

