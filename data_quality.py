from pyspark.sql.functions import (
    col,
    count,
    length,
    lit,
    when,
)

# ============================================================
# Required Fields
# ============================================================

REQUIRED_FIELDS = [
    "jobscope_job_id",
    "job_id",
    "title",
    "company_name",
    "location",
    "description",
]


# ============================================================
# 1. Validate Required Fields
# ============================================================

def validate_required_fields(jobs_df):

    quality_reason = lit(None).cast("string")

    for field in REQUIRED_FIELDS:

        invalid_condition = (
            col(field).isNull()
            | (length(col(field)) == 0)
        )

        quality_reason = when(
            invalid_condition,
            lit(f"missing required field: {field}")
        ).otherwise(
            quality_reason
        )

    jobs_df = jobs_df.withColumn(
        "quality_reason",
        quality_reason
    )

    jobs_df = jobs_df.withColumn(
        "quality_status",
        when(
            col("quality_reason").isNotNull(),
            lit("rejected")
        ).otherwise(
            lit("valid")
        )
    )

    return jobs_df


# ============================================================
# 2. Validate Duplicate Job IDs
# ============================================================

def validate_duplicates(jobs_df):

    # --------------------------------------------------------
    # Duplicate JobScope IDs
    # --------------------------------------------------------

    duplicate_jobscope_ids = (
        jobs_df
        .filter(col("jobscope_job_id").isNotNull())
        .groupBy("jobscope_job_id")
        .agg(count("*").alias("jobscope_id_count"))
        .filter(col("jobscope_id_count") > 1)
        .select("jobscope_job_id")
    )

    jobs_df = (
        jobs_df
        .join(
            duplicate_jobscope_ids.withColumn(
                "duplicate_jobscope_id",
                lit(True)
            ),
            on="jobscope_job_id",
            how="left"
        )
    )

    # --------------------------------------------------------
    # Duplicate SerpApi Job IDs
    # --------------------------------------------------------

    duplicate_job_ids = (
        jobs_df
        .filter(col("job_id").isNotNull())
        .groupBy("job_id")
        .agg(count("*").alias("job_id_count"))
        .filter(col("job_id_count") > 1)
        .select("job_id")
    )

    jobs_df = (
        jobs_df
        .join(
            duplicate_job_ids.withColumn(
                "duplicate_job_id",
                lit(True)
            ),
            on="job_id",
            how="left"
        )
    )

    # --------------------------------------------------------
    # Mark Duplicate Records
    # --------------------------------------------------------

    jobs_df = jobs_df.withColumn(
        "quality_reason",
        when(
            col("duplicate_jobscope_id") == True,
            lit("duplicate JobScope job ID")
        )
        .when(
            col("duplicate_job_id") == True,
            lit("duplicate SerpApi job ID")
        )
        .otherwise(
            col("quality_reason")
        )
    )

    jobs_df = jobs_df.withColumn(
        "quality_status",
        when(
            col("quality_reason").isNotNull(),
            lit("rejected")
        )
        .otherwise(
            col("quality_status")
        )
    )

    # --------------------------------------------------------
    # Remove Temporary Columns
    # --------------------------------------------------------

    jobs_df = jobs_df.drop(
        "duplicate_jobscope_id",
        "duplicate_job_id",
    )

    return jobs_df

# ============================================================
# 3. Validate Salary
# ============================================================


def validate_salary(jobs_df):

    invalid_salary_condition = (
        (
            col("annual_salary_min").isNotNull()
            & col("annual_salary_max").isNotNull()
            & (
                col("annual_salary_min")
                > col("annual_salary_max")
            )
        )
        |
        (
            col("annual_salary_min").isNotNull()
            & (col("annual_salary_min") < 0)
        )
        |
        (
            col("annual_salary_max").isNotNull()
            & (col("annual_salary_max") < 0)
        )
    )

    jobs_df = jobs_df.withColumn(
        "quality_reason",
        when(
            invalid_salary_condition,
            lit("invalid salary range")
        ).otherwise(
            col("quality_reason")
        )
    )

    jobs_df = jobs_df.withColumn(
        "quality_status",
        when(
            col("quality_reason").isNotNull(),
            lit("rejected")
        ).otherwise(
            col("quality_status")
        )
    )

    return jobs_df

# ============================================================
# 4. Validate Employment Type
# ============================================================


VALID_EMPLOYMENT_TYPES = [
    "full-time",
    "part-time",
    "contract",
    "temporary",
    "internship",
]


def validate_employment_type(jobs_df):

    invalid_employment_condition = (
        col("employment_type").isNotNull()
        & ~col("employment_type").isin(
            VALID_EMPLOYMENT_TYPES
        )
    )

    jobs_df = jobs_df.withColumn(
        "quality_reason",
        when(
            invalid_employment_condition,
            lit("invalid employment type")
        ).otherwise(
            col("quality_reason")
        )
    )

    jobs_df = jobs_df.withColumn(
        "quality_status",
        when(
            col("quality_reason").isNotNull(),
            lit("rejected")
        ).otherwise(
            col("quality_status")
        )
    )

    return jobs_df

# ============================================================
# 5. Run All Data Quality Checks
# ============================================================


def validate_jobs(jobs_df):

    jobs_df = validate_required_fields(jobs_df)

    jobs_df = validate_duplicates(jobs_df)

    jobs_df = validate_salary(jobs_df)

    jobs_df = validate_employment_type(jobs_df)

    return jobs_df


# ============================================================
# 6. Print Quality Report
# ============================================================

def print_quality_report(jobs_df):

    total_jobs = jobs_df.count()

    valid_jobs = (
        jobs_df
        .filter(col("quality_status") == "valid")
        .count()
    )

    rejected_jobs = (
        jobs_df
        .filter(col("quality_status") == "rejected")
        .count()
    )

    print("\n==============================")
    print("DATA QUALITY REPORT")
    print("==============================")

    print(f"Total jobs:     {total_jobs}")
    print(f"Valid jobs:     {valid_jobs}")
    print(f"Rejected jobs:  {rejected_jobs}")

    print("\nRejection reasons:")

    (
        jobs_df
        .filter(col("quality_status") == "rejected")
        .groupBy("quality_reason")
        .count()
        .orderBy(col("count").desc())
        .show(truncate=False)
    )


# ============================================================
# 7. Get Valid Jobs
# ============================================================

def get_valid_jobs(jobs_df):

    return jobs_df.filter(
        col("quality_status") == "valid"
    )


# ============================================================
# 8. Get Rejected Jobs
# ============================================================

def get_rejected_jobs(jobs_df):

    return jobs_df.filter(
        col("quality_status") == "rejected"
    )
