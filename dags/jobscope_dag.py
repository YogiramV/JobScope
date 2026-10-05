import sys
import logging

from datetime import datetime, timedelta, date

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


# ============================================================
# Logging
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# JobScope Project Paths
# ============================================================

JOB_SCOPE_PATH = "/home/yogi/workspace/DataScience/Projects/JobScope"
DATABASE_PATH = "/home/yogi/workspace/DataScience/Projects/JobScope/database"

sys.path.insert(0, JOB_SCOPE_PATH)
sys.path.insert(0, DATABASE_PATH)


# ============================================================
# JobScope Imports
# ============================================================

from jobs_fetcher import get_jobs
from jobs_processor import process_jobs
from database.loader import load_jobs
from skill_extractor import extract_all_job_skills


# ============================================================
# Search Configuration
# ============================================================

ROLE = "Data Engineer"
SEARCH_LOCATION = "Coimbatore"
COUNTRY = "India"


# ============================================================
# Data Paths
# ============================================================

BUCKET_NAME = "jobscope-data"


# ============================================================
# Task 1 - Fetch Jobs
# ============================================================

def fetch_job_data():

    logger.info(
        "Starting job ingestion for role=%s, location=%s",
        ROLE,
        SEARCH_LOCATION
    )

    get_jobs(
        ROLE,
        SEARCH_LOCATION
    )

    logger.info("Job ingestion completed successfully.")


# ============================================================
# Task 2 - Process Jobs
# ============================================================

def process_job_data():

    today = str(date.today())

    filename = (
        ROLE + "_" + SEARCH_LOCATION
    ).lower().replace(" ", "_") + ".json"

    raw_data_path = (
        f"s3a://{BUCKET_NAME}/"
        f"raw_data/{today}/"
        f"{filename}"
    )

    processed_data_path = (
        f"s3a://{BUCKET_NAME}/"
        f"processed_data/{today}/"
    )

    logger.info(
        "Starting PySpark processing."
    )

    logger.info(
        "Raw data path: %s",
        raw_data_path
    )

    logger.info(
        "Processed data path: %s",
        processed_data_path
    )

    process_jobs(
        raw_data_path,
        processed_data_path
    )

    logger.info(
        "PySpark processing completed successfully."
    )


# ============================================================
# Task 3 - Load Jobs
# ============================================================

def load_job_data():

    today = str(date.today())

    processed_data_path = (
        f"s3a://{BUCKET_NAME}/"
        f"processed_data/{today}/"
    )

    logger.info(
        "Starting PostgreSQL job loading."
    )

    logger.info(
        "Processed data path: %s",
        processed_data_path
    )

    load_jobs(
        processed_path=processed_data_path,
        role=ROLE,
        search_location=SEARCH_LOCATION,
        country=COUNTRY
    )

    logger.info(
        "PostgreSQL job loading completed successfully."
    )


# ============================================================
# Task 4 - Extract Skills
# ============================================================

def extract_job_skills():

    logger.info(
        "Starting job skill extraction."
    )

    extract_all_job_skills()

    logger.info(
        "Job skill extraction completed successfully."
    )


# ============================================================
# DAG
# ============================================================

with DAG(
    dag_id="jobscope_dag",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    # --------------------------------------------------------
    # Fetch Jobs
    # --------------------------------------------------------

    fetch_jobs_task = PythonOperator(
        task_id="fetch_jobs",
        python_callable=fetch_job_data,
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    # --------------------------------------------------------
    # Process Jobs
    # --------------------------------------------------------

    process_jobs_task = PythonOperator(
        task_id="process_jobs",
        python_callable=process_job_data,
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    # --------------------------------------------------------
    # Load Jobs
    # --------------------------------------------------------

    load_jobs_task = PythonOperator(
        task_id="load_jobs",
        python_callable=load_job_data,
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    # --------------------------------------------------------
    # Extract Skills
    # --------------------------------------------------------

    extract_skills_task = PythonOperator(
        task_id="extract_skills",
        python_callable=extract_job_skills,
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    # --------------------------------------------------------
    # Task Dependency
    # --------------------------------------------------------

    (
        fetch_jobs_task
        >> process_jobs_task
        >> load_jobs_task
        >> extract_skills_task
    )