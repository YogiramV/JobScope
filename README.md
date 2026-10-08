# JobScope

JobScope is a data engineering and analytics project that collects job-market data from Google Jobs, processes and transforms the data using PySpark, stores structured data in PostgreSQL, extracts skills from job descriptions, and presents the results through an interactive Streamlit dashboard.

The project is designed as an automated data pipeline rather than a simple job-search application.

---

## Features

* Fetch job listings using SerpApi Google Jobs
* Support multiple role and location search configurations
* Store raw job responses in AWS S3
* Process and clean job data using PySpark
* Generate stable job identifiers
* Normalize employment types and salary information
* Store structured job data in PostgreSQL
* Maintain company and location relationships
* Maintain a normalized skill dictionary
* Extract skills from job descriptions
* Track job-skill relationships
* Perform job-market analytics
* Interactive Streamlit dashboard
* Automated pipeline orchestration using Apache Airflow
* Dockerized development environment
* Incremental processing and duplicate handling
* AWS S3 integration for raw and processed data

---

## Architecture

```text
                         ┌────────────────────┐
                         │   Search Config    │
                         │ Role + Location    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      Airflow       │
                         │  Pipeline Manager  │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      SerpApi       │
                         │    Google Jobs     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │     Raw JSON       │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      AWS S3        │
                         │    Raw Storage     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      PySpark      │
                         │ Data Processing    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   Processed Data   │
                         │      Parquet       │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │    PostgreSQL      │
                         │ Structured Storage │
                         └─────────┬──────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ Skill Extraction │          │    Analytics     │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                         ┌────────────────────┐
                         │     Streamlit      │
                         │     Dashboard      │
                         └────────────────────┘
```

---

## Tech Stack

| Component              | Technology              |
| ---------------------- | ----------------------- |
| Job Data Source        | SerpApi / Google Jobs   |
| Data Processing        | PySpark                 |
| Data Storage           | PostgreSQL              |
| Object Storage         | AWS S3                  |
| Workflow Orchestration | Apache Airflow          |
| Dashboard              | Streamlit               |
| Containerization       | Docker / Docker Compose |
| Programming Language   | Python                  |
| Data Analysis          | Pandas / SQL            |
| API                    | SerpApi                 |

---

## Pipeline

The Airflow pipeline consists of the following tasks:

```text
fetch_jobs
    ↓
process_jobs
    ↓
load_jobs
    ↓
load_skills
    ↓
extract_skills
```

### 1. Fetch Jobs

Airflow retrieves the active search configurations from PostgreSQL.

Each configuration contains:

* Role
* Location
* Country

The pipeline then queries SerpApi Google Jobs for each active configuration.

The raw API response is saved locally and uploaded to AWS S3.

---

### 2. Process Jobs

PySpark reads the raw JSON data and performs transformations such as:

* Extracting job records
* Normalizing text fields
* Cleaning job titles
* Cleaning company names
* Cleaning locations
* Normalizing employment types
* Extracting salary information
* Converting monthly salaries to annual values
* Handling missing values
* Detecting duplicates
* Generating stable JobScope job IDs

Processed data is stored as Parquet.

---

### 3. Load Jobs

The processed job data is loaded into PostgreSQL.

The database maintains relationships between:

* Jobs
* Companies
* Locations
* Search configurations

Duplicate jobs are handled using the generated stable job ID.

---

### 4. Load Skills

The normalized skill dictionary is loaded into the PostgreSQL `skills` table.

The dictionary contains:

* Original skill name
* Normalized skill name

Existing skills are not inserted again because the database uses conflict handling.

---

### 5. Extract Skills

Job descriptions are analyzed against the skill dictionary.

Detected skills are associated with individual jobs through the `job_skills` relationship table.

This allows the dashboard to answer questions such as:

* Which skills are most frequently requested?
* Which skills are associated with a particular role?
* Which skills occur together?
* What skills are requested in a particular location?

---

# Database

JobScope uses PostgreSQL for structured storage.

## Main Tables

### `companies`

Stores unique companies.

```text
company_id
company_name
created_at
```

### `locations`

Stores normalized job locations.

```text
location_id
city
state
country
location_name
created_at
```

### `search_configurations`

Stores the job searches that the pipeline should perform.

```text
search_id
role
location
country
created_at
is_active
```

### `jobs`

Stores the normalized job listings.

Important fields include:

```text
jobscope_job_id
job_id
title
company_id
location_id
description
via
source_link
apply_options
employment_type
annual_salary_min
annual_salary_max
first_seen_at
last_seen_at
```

### `job_searches`

Associates jobs with the searches that discovered them.

### `skills`

Stores the normalized skill dictionary.

### `job_skills`

Creates the many-to-many relationship between jobs and skills.

```text
Job → many skills
Skill → many jobs
```

---

# AWS S3 Structure

Raw job responses are stored in S3 using the ingestion date.

```text
jobscope-data/
└── raw_data/
    └── YYYY-MM-DD/
        ├── data_engineer_chennai.json
        ├── data_analyst_chennai.json
        └── ...
```

Processed data is stored separately from the raw source data.

Keeping raw data allows the processing layer to be reproduced without querying the external API again.

---

# Airflow

Airflow is responsible for orchestrating the complete pipeline.

The DAG currently uses:

```text
fetch_jobs
    ↓
process_jobs
    ↓
load_jobs
    ↓
load_skills
    ↓
extract_skills
```

Airflow provides:

* Task dependencies
* Retry handling
* Task logs
* Pipeline execution
* Failure visibility
* Scheduled execution

The DAG is currently configured for manual execution rather than continuous scheduling.

---

# Streamlit Dashboard

The Streamlit application reads processed information from PostgreSQL rather than directly querying SerpApi.

The dashboard provides analytics such as:

* Total jobs
* Jobs by role
* Jobs by location
* Company job counts
* Employment type distribution
* Salary information
* Skill demand
* Skill demand by role
* Skill demand by location
* Skill combinations
* Job exploration

Search configurations can also be managed through the application.

---

# Docker

JobScope uses Docker Compose to run the main application components.

The environment includes:

```text
PostgreSQL
Airflow
Streamlit
```

PySpark and the required Java runtime are included in the Airflow image.

The project also mounts the host AWS credentials directory into the Airflow container so that boto3 can authenticate with AWS without storing credentials in the repository.

The AWS credential mapping is portable across Linux/macOS machines:

```yaml
- ${HOME}/.aws:/home/airflow/.aws:ro
```

---

# Setup

## Prerequisites

Install the following:

* Git
* Docker
* Docker Compose
* AWS CLI
* An AWS account with access to the required S3 bucket
* A SerpApi account and API key

---

## Clone the Repository

```bash
git clone <repository-url>
cd JobScope
```

---

## Configure Environment Variables

Create a `.env` file from `.env.example`.

```env
SERPAPI_API_KEY=your_serpapi_api_key

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jobscope
POSTGRES_USER=jobscope
POSTGRES_PASSWORD=jobscope

JOB_SCOPE_S3_BUCKET=jobscope-data
```

Do not commit `.env` to Git.

---

# AWS Configuration

JobScope uses AWS S3 for data storage.

Configure AWS credentials on the host machine using the AWS CLI.

The credentials should be available under:

```text
~/.aws/
```

For example:

```text
~/.aws/
├── credentials
└── config
```

The Airflow container accesses these credentials through the read-only Docker volume:

```yaml
${HOME}/.aws:/home/airflow/.aws:ro
```

AWS credentials must never be committed to the repository.

---

# Run with Docker

Start the complete environment:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

The main services are:

```text
PostgreSQL
Airflow
Streamlit
```

---

# Access the Applications

### Streamlit

```text
http://localhost:8501
```

### Airflow

```text
http://localhost:8080
```

Airflow can be used to trigger and monitor the JobScope pipeline.

---

# Running the Pipeline

From the Airflow interface, trigger the JobScope DAG.

The expected task sequence is:

```text
fetch_jobs
    ↓
process_jobs
    ↓
load_jobs
    ↓
load_skills
    ↓
extract_skills
```

A successful run means the complete pipeline has:

1. Retrieved job data
2. Stored raw data
3. Processed the data
4. Loaded jobs into PostgreSQL
5. Loaded the skill dictionary
6. Extracted skills from job descriptions
7. Created job-skill relationships

---

# Search Configuration

Job searches are stored in PostgreSQL rather than hardcoded into the pipeline.

A configuration contains:

```text
Role
Location
Country
Active/Inactive status
```

This allows additional searches to be added without modifying the Airflow DAG.

For example:

```text
Data Analyst → Chennai → India
Data Engineer → Chennai → India
Data Scientist → Bangalore → India
```

Only active configurations are processed by the ingestion pipeline.

---

# Data Quality

The processing pipeline performs validation for important fields and transformations.

Examples include:

* Required job fields
* Stable job IDs
* Duplicate detection
* Salary validation
* Location normalization
* Employment type normalization
* Missing-value handling
* Skill relationship validation

Invalid or unexpected records can be identified during processing rather than silently entering the database.

---

# Incremental Processing

JobScope generates a stable identifier for jobs using normalized job information.

This allows the pipeline to identify jobs that have already been processed and reduces duplicate records when the same job appears in multiple ingestion runs.

The database also uses primary keys, unique constraints, and conflict handling to protect against duplicate data.

---

# Project Structure

```text
JobScope/
│
├── airflow/
│   ├── Dockerfile
│   └── requirements.txt
│
├── dags/
│   └── jobscope_dag.py
│
├── database/
│   ├── connection.py
│   └── ...
│
├── resources/
│   └── jobscope_skill_dictionary_normalized.csv
│
├── raw_data/
│
├── processed_data/
│
├── jobs_fetcher.py
├── jobs_processor.py
├── load_jobs.py
├── load_skills.py
├── extract_skills.py
├── analytics.py
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

# Security

The following files and credentials should never be committed:

```text
.env
AWS credentials
SerpApi API keys
Other secrets
```

AWS authentication is handled through the host AWS credential configuration.

---

# Limitations

### SerpApi Dependency

Job data collection depends on SerpApi and its available API quota.

The number of searches that can be performed is therefore limited by the SerpApi account and plan.

### Job Data Availability

Google Jobs does not guarantee that every job contains:

* Salary information
* Employment type
* Complete descriptions
* Consistent location information

The pipeline therefore treats some fields as optional.

### Skill Extraction

Skill extraction currently depends on the maintained skill dictionary.

Skills that are not present in the dictionary may not be detected.

### Job Freshness

Job listings can change or disappear from external sources. The data stored by JobScope represents what was available when the ingestion occurred.

---

# Future Improvements

Possible future improvements include:

* More advanced skill extraction
* Automated discovery of unknown skills
* Improved job deduplication
* Additional job sources
* Historical job-market analysis
* More sophisticated salary normalization
* Pipeline monitoring
* Automated data-quality reporting
* Cloud deployment
* Scheduled production execution
* Additional dashboard visualizations

---

# Project Goal

JobScope was built to explore the practical workflow of a data engineering and analytics system:

```text
API Data Collection
        ↓
Object Storage
        ↓
Distributed Data Processing
        ↓
Relational Data Storage
        ↓
Data Transformation
        ↓
Analytics
        ↓
Visualization
        ↓
Workflow Orchestration
```

The project focuses on building an end-to-end pipeline rather than only creating a dashboard from an existing dataset.
