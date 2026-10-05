import sys
import logging

from datetime import datetime, timedelta

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

from jobs_processor import process_jobs
from loader import load_jobs
from skill_extractor import extract_all_job_skills


# ============================================================
# S3 Paths
# ============================================================

RAW_DATA_PATH = (
    "s3a://jobscope-data/"
    "raw_data/2026-09-28/"
    "data_engineer_coimbatore.json"
)

PROCESSED_DATA_PATH = (
    "s3a://jobscope-data/"
    "processed_data/airflow_test/"
)


# ============================================================
# Task Functions
# ============================================================

def process_job_data():

    logger.info("Starting JobScope PySpark processing.")

    process_jobs(
        RAW_DATA_PATH,
        PROCESSED_DATA_PATH
    )

    logger.info("JobScope PySpark processing completed successfully.")


def load_job_data():

    logger.info("Starting PostgreSQL job loading.")

    load_jobs(
        processed_path=PROCESSED_DATA_PATH,
        role="Data Engineer",
        search_location="Coimbatore",
        country="India"
    )

    logger.info("PostgreSQL job loading completed successfully.")


def extract_job_skills():

    logger.info("Starting job skill extraction.")

    extract_all_job_skills()

    logger.info("Job skill extraction completed successfully.")


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

    process_jobs_task >> load_jobs_task >> extract_skills_task