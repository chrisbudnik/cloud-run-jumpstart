import logging
from typing import Literal
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from fastapi import HTTPException
from fastapi.responses import JSONResponse


# BigQuery actions logger
logger = logging.getLogger(__name__)


def dataframe_to_bigquery(
        client: bigquery.Client,
        table_id: str, 
        data: pd.DataFrame, 
        schema: list[bigquery.SchemaField] = None,
        partition_field: str = None,
        clustering_fields: list[str] = None,
        write_disposition: Literal[
            "WRITE_TRUNCATE", "WRITE_APPEND", "WRITE_EMPTY"
            ] = "WRITE_APPEND",
    ) -> Literal["export-completed", "missing-data"]:
    """

    """
    # If empty - warning of missing data
    if data.empty: 
        logger.warning("No data to upload to BigQuery.")
        return "missing-data"
    
    # Connect to BigQuery
    table_ref = bigquery.TableReference.from_string(table_id)

    # Export data to BQ table with date partitioning
    try:
        job_config = bigquery.LoadJobConfig(
            write_disposition = write_disposition
        )

        if schema:
            job_config.schema = schema

        if clustering_fields:
            job_config.clustering_fields = clustering_fields

        if partition_field:
            job_config.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field
            )

        job = client.load_table_from_dataframe(data, table_ref, job_config=job_config)
        job.result()

        logger.info(f"Data uploaded to BigQuery table '{table_id}' successfully.")

    except Exception as e:
        logger.error(f"Failed to upload data to BigQuery. {e}")
        raise HTTPException(status_code=500, detail="Failed to upload data to BigQuery.")

    return "export-completed"
    

def check_if_table_exists(
        client: bigquery.Client, dataset_id: str, table_id: str
    ) -> bool:
    """
    Check if a table exists in BigQuery using the full table ID.

    Args:
    client (bigquery.Client): The BigQuery client.
    dataset_id (str): The dataset ID.
    table_id (str): The table ID.

    Returns:
    bool: True if the table exists, False otherwise.
    """
    try:
        full_table_id = f"{client.project}.{dataset_id}.{table_id}"
        client.get_table(full_table_id)  
        return True
    
    except NotFound as e:
        logger.error(f"Table '{full_table_id}' not found in BigQuery. {e}")
        return False
    
def send_data_to_bigquery(
        client: bigquery.Client, 
        dataset_id: str, 
        table_id: str, 
        data: dict
    ) -> JSONResponse:
    """
    
    """
    # Check if the table exists in dataset
    if not check_if_table_exists(client, dataset_id, table_id):
        raise HTTPException(status_code=404, detail="Table not found in BigQuery.")
    
    # Create a table reference, and insert the data
    table_ref = client.dataset(dataset_id).table(table_id)
    errors = client.insert_rows_json(table_ref, [data])  
    
    # Return errors if any
    if errors:
        logger.error(f"Errors while inserting into BigQuery: {errors}")
        raise HTTPException(status_code=404, detail="Failed to send data to BigQuery.")
    
    logger.info("Data sent to BigQuery successfully.")
    return JSONResponse({"message": "Data sent to BigQuery successfully."}, status_code=200)



