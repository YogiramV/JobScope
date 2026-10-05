from pyspark.sql.functions import (
    col,
    concat_ws,
    explode,
    expr,
    regexp_replace,
    sha2,
    split,
    trim,
    when,
)
from pyspark.sql import SparkSession

# ============================================================
# Configuration
# ============================================================

BUCKET_NAME = "jobscope-data"


def process_jobs(raw_data_path, processed_data_path):

    # ============================================================
    # 1. Spark Session
    # ============================================================

    spark = (
        SparkSession.builder
        .appName("JobScope")
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.5.0",
        )
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.profile.ProfileCredentialsProvider",
        )
        .getOrCreate()
    )

    # ============================================================
    # 2. Read Raw Job Data from S3
    # ============================================================

    df = (
        spark.read
        .option("multiLine", True)
        .json(raw_data_path)
    )

    # ============================================================
    # 3. Extract Individual Jobs
    # ============================================================

    jobs_df = df.select(
        explode("jobs_results").alias("job")
    )

    # ============================================================
    # 4. Select Required Fields
    # ============================================================

    jobs_df = jobs_df.select(
        "job.job_id",
        "job.title",
        "job.company_name",
        "job.location",
        "job.description",
        "job.via",
        "job.source_link",
        "job.extensions",
        "job.apply_options",
    )

    # ============================================================
    # 5. Basic Inspection
    # ============================================================

    print("Number of jobs:", jobs_df.count())

    # ============================================================
    # 6. Text Normalization
    # ============================================================

    text_columns = [
        "title",
        "company_name",
        "location",
        "description",
        "via",
    ]

    for column_name in text_columns:
        jobs_df = jobs_df.withColumn(
            column_name,
            trim(col(column_name)),
        )

    # ============================================================
    # 7. Extract Employment Type
    # ============================================================

    jobs_df = jobs_df.withColumn(
        "employment_type",
        expr("""
            filter(
                extensions,
                x -> lower(x) LIKE '%full%'
                    OR lower(x) LIKE '%part%'
                    OR lower(x) LIKE '%contract%'
                    OR lower(x) LIKE '%temporary%'
                    OR lower(x) LIKE '%intern%'
            )[0]
        """),
    )

    jobs_df = jobs_df.withColumn(
        "employment_type",
        trim(col("employment_type")),
    )

    # ============================================================
    # 8. Extract Salary
    # ============================================================

    jobs_df = jobs_df.withColumn(
        "salary",
        expr("""
            get(
                filter(
                    extensions,
                    x -> x LIKE '%₹%'
                ),
                0
            )
        """),
    )

    # ============================================================
    # 9. Determine Salary Period
    # ============================================================

    jobs_df = jobs_df.withColumn(
        "salary_period",
        when(
            col("salary").contains("year"),
            "year",
        )
        .when(
            col("salary").contains("month"),
            "month",
        )
        .otherwise(None),
    )

    # ============================================================
    # 10. Extract Salary Range
    # ============================================================

    jobs_df = jobs_df.withColumn(
        "salary_min",
        regexp_replace(
            split(col("salary"), "–")[0],
            "₹",
            "",
        ),
    )

    jobs_df = jobs_df.withColumn(
        "salary_max",
        regexp_replace(
            split(col("salary"), "–")[1],
            "₹| a year| a month",
            "",
        ),
    )

    # ============================================================
    # 11. Convert Salary to Numeric Values
    # ============================================================

    jobs_df = jobs_df.withColumn(
        "salary_min_numeric",
        when(
            col("salary_min").endswith("K"),
            regexp_replace(
                col("salary_min"),
                "K",
                "",
            ).cast("double") * 1000,
        )
        .when(
            col("salary_min").endswith("L"),
            regexp_replace(
                col("salary_min"),
                "L",
                "",
            ).cast("double") * 100000,
        )
        .otherwise(None),
    )

    jobs_df = jobs_df.withColumn(
        "salary_max_numeric",
        when(
            col("salary_max").endswith("K"),
            regexp_replace(
                col("salary_max"),
                "K",
                "",
            ).cast("double") * 1000,
        )
        .when(
            col("salary_max").endswith("L"),
            regexp_replace(
                col("salary_max"),
                "L",
                "",
            ).cast("double") * 100000,
        )
        .otherwise(None),
    )

    # ============================================================
    # 12. Calculate Annual Salary
    # ============================================================

    jobs_df = jobs_df.withColumn(
        "annual_salary_min",
        when(
            col("salary_period") == "year",
            col("salary_min_numeric"),
        )
        .when(
            col("salary_period") == "month",
            col("salary_min_numeric") * 12,
        )
        .otherwise(None),
    )

    jobs_df = jobs_df.withColumn(
        "annual_salary_max",
        when(
            col("salary_period") == "year",
            col("salary_max_numeric"),
        )
        .when(
            col("salary_period") == "month",
            col("salary_max_numeric") * 12,
        )
        .otherwise(None),
    )

    # ============================================================
    # 13. Generate JobScope Job ID
    # ============================================================

    jobs_df = jobs_df.withColumn(
        "jobscope_job_id",
        sha2(
            concat_ws(
                "||",
                col("title"),
                col("company_name"),
                col("location"),
            ),
            256,
        ),
    )

    # ============================================================
    # 14. Data Quality Checks
    # ============================================================

    print("\nInvalid salary ranges:")

    jobs_df.filter(
        col("annual_salary_min") > col("annual_salary_max")
    ).select(
        "title",
        "salary",
        "annual_salary_min",
        "annual_salary_max",
    ).show(truncate=False)

    print("\nJobs with missing required fields:")

    jobs_df.filter(
        col("job_id").isNull()
        | col("title").isNull()
        | col("company_name").isNull()
        | col("location").isNull()
        | col("description").isNull()
    ).select(
        "job_id",
        "title",
        "company_name",
        "location",
    ).show(truncate=False)

    print("\nDuplicate SerpApi job IDs:")

    jobs_df.groupBy("job_id") \
        .count() \
        .filter(col("count") > 1) \
        .show(truncate=False)

    print("\nDuplicate JobScope IDs:")

    jobs_df.groupBy("jobscope_job_id") \
        .count() \
        .filter(col("count") > 1) \
        .show(truncate=False)

    print("\nMissing JobScope IDs:")

    print(
        jobs_df.filter(
            col("jobscope_job_id").isNull()
        ).count()
    )

    # ============================================================
    # 15. Final Inspection
    # ============================================================

    jobs_df.select(
        "jobscope_job_id",
        "job_id",
        "title",
        "company_name",
        "location",
        "employment_type",
        "salary",
        "salary_period",
        "salary_min_numeric",
        "salary_max_numeric",
        "annual_salary_min",
        "annual_salary_max",
    ).show(
        20,
        truncate=False,
    )

    # ============================================================
    # 16. Create Processed Dataset
    # ============================================================

    processed_jobs_df = jobs_df.select(
        "jobscope_job_id",
        "job_id",
        "title",
        "company_name",
        "location",
        "description",
        "via",
        "source_link",
        "apply_options",
        "employment_type",
        "annual_salary_min",
        "annual_salary_max",
    )

    # ============================================================
    # 17. Validate Processed Dataset
    # ============================================================

    print("Original jobs:", jobs_df.count())
    print("Processed jobs:", processed_jobs_df.count())

    processed_jobs_df.printSchema()

    # ============================================================
    # 18. Write Processed Data to S3
    # ============================================================

    processed_jobs_df.write \
        .mode("overwrite") \
        .parquet(processed_data_path)

    # ============================================================
    # 19. Stop Spark Session
    # ============================================================

    spark.stop()


if __name__ == "__main__":
    process_jobs(
        f"s3a://{BUCKET_NAME}/"
        "raw_data/2026-09-24/data_engineer_coimbatore.json",
        f"s3a://{BUCKET_NAME}/"
        "processed_data/2026-09-28/",
    )
