import logging
from typing import Literal
import pandas as pd
from google.cloud import bigquery
from fastapi import HTTPException

# BigQuery actions logger
logger = logging.getLogger(__name__)


def dataframe_to_bigquery(
        client: bigquery.Client,
        table_id: str, 
        data: pd.DataFrame, 
        schema: list[bigquery.SchemaField] = None,
        partition_field: str = None,
        clustering_fields: list[str] = None,
        write_disposition: Literal["WRITE_TRUNCATE", "WRITE_APPEND", "WRITE_EMPTY"] = "WRITE_APPEND",
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