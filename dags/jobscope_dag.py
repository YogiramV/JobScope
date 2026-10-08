from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from datetime import datetime, timedelta, date
import logging
import sys
import os


# ============================================================
# Logging
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# JobScope Project Paths
# ============================================================

JOB_SCOPE_PATH = os.getenv(
    "JOB_SCOPE_PATH",
    "/home/yogi/workspace/DataScience/Projects/JobScope"
)

DATABASE_PATH = os.path.join(
    JOB_SCOPE_PATH,
    "database"
)

sys.path.insert(0, JOB_SCOPE_PATH)
sys.path.insert(0, DATABASE_PATH)


# ============================================================
# JobScope Imports
# ============================================================

from database.load_skills import load_skills
from skill_extractor import extract_all_job_skills
from database.analytics import get_active_search_configurations
from database.loader import load_jobs
from jobs_processor import process_jobs
from jobs_fetcher import get_jobs

# ============================================================
# Data Paths
# ============================================================

BUCKET_NAME = os.getenv(
    "JOB_SCOPE_S3_BUCKET",
    "jobscope-data"
)

# ============================================================
# Task 1 - Fetch Jobs
# ============================================================


def fetch_job_data():

    configurations = get_active_search_configurations()

    if not configurations:
        logger.warning(
            "No active search configurations found."
        )
        return

    logger.info(
        "Found %d active search configuration(s).",
        len(configurations)
    )

    for search_id, role, location, country in configurations:

        logger.info(
            "Starting job ingestion: "
            "search_id=%s, role=%s, location=%s, country=%s",
            search_id,
            role,
            location,
            country
        )

        get_jobs(
            role,
            location
        )

        logger.info(
            "Job ingestion completed: "
            "search_id=%s, role=%s, location=%s",
            search_id,
            role,
            location
        )


# ============================================================
# Task 2 - Process Jobs
# ============================================================

def process_job_data():

    today = str(date.today())

    configurations = get_active_search_configurations()

    if not configurations:
        logger.warning(
            "No active search configurations found."
        )
        return

    for search_id, role, location, country in configurations:

        filename = (
            role + "_" + location
        ).lower().replace(" ", "_") + ".json"

        raw_data_path = (
            f"s3a://{BUCKET_NAME}/"
            f"raw_data/{today}/"
            f"{filename}"
        )

        processed_data_path = (
            f"s3a://{BUCKET_NAME}/"
            f"processed_data/{today}/"
            f"{role}_{location}".lower().replace(" ", "_") + "/"
        )

        logger.info(
            "Starting PySpark processing: "
            "search_id=%s, role=%s, location=%s",
            search_id,
            role,
            location
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
            "PySpark processing completed: "
            "search_id=%s, role=%s, location=%s",
            search_id,
            role,
            location
        )


# ============================================================
# Task 3 - Load Jobs
# ============================================================

def load_job_data():

    today = str(date.today())

    configurations = get_active_search_configurations()

    if not configurations:
        logger.warning(
            "No active search configurations found."
        )
        return

    for search_id, role, location, country in configurations:

        processed_data_path = (
            f"s3a://{BUCKET_NAME}/"
            f"processed_data/{today}/"
            f"{role}_{location}".lower().replace(" ", "_") + "/"
        )

        logger.info(
            "Starting PostgreSQL job loading: "
            "search_id=%s, role=%s, location=%s",
            search_id,
            role,
            location
        )

        logger.info(
            "Processed data path: %s",
            processed_data_path
        )

        load_jobs(
            processed_path=processed_data_path,
            role=role,
            search_location=location,
            country=country,
            observation_date=date.today()
        )

        logger.info(
            "PostgreSQL job loading completed: "
            "search_id=%s, role=%s, location=%s",
            search_id,
            role,
            location
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
    # Load Skills
    # --------------------------------------------------------

    load_skills_task = PythonOperator(
        task_id="load_skills",
        python_callable=load_skills,
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
        >> load_skills_task
        >> extract_skills_task
    )
