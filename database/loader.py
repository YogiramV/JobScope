from pyspark.sql import SparkSession
from queries import (
    get_or_create_company,
    get_or_create_location,
    get_or_create_search_configuration,
    insert_or_update_job,
    add_job_to_search
)


INDIAN_STATES = {
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry"
}


def load_jobs(
    processed_path,
    role,
    search_location,
    country
):

    spark = SparkSession.builder \
        .appName("JobScope PostgreSQL Loader") \
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.5.0"
        ) \
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.profile.ProfileCredentialsProvider"
        ) \
        .getOrCreate()

    try:
        # Read processed jobs
        jobs_df = spark.read.parquet(processed_path)

        # Get or create search configuration
        search_id = get_or_create_search_configuration(
            role=role,
            location=search_location,
            country=country
        )

        # Process each job
        for row in jobs_df.collect():

            job = row.asDict()

            # Get company
            company_id = get_or_create_company(
                company_name=job["company_name"]
            )

            # Parse location
            location_parts = [
                part.strip()
                for part in job["location"].split(",")
                if part.strip()
            ]

            if len(location_parts) >= 2:

                # Example:
                # Coimbatore, Tamil Nadu
                city = location_parts[0]
                state = location_parts[1]

            elif len(location_parts) == 1:

                location = location_parts[0]

                # Example:
                # India
                if location.lower() == country.lower():
                    city = None
                    state = None

                # Example:
                # Tamil Nadu
                elif any(
                    location.lower() == state_name.lower()
                    for state_name in INDIAN_STATES
                ):
                    city = None
                    state = location

                # Example:
                # Coimbatore
                else:
                    city = location
                    state = None

            else:

                city = None
                state = None

            # Get location
            location_id = get_or_create_location(
                city=city,
                state=state,
                country=country
            )

            print("\n--- JOB DATA ---")

            for key, value in job.items():
                if isinstance(value, str):
                    print(f"{key}: {len(value)} characters")

            # Insert or update job
            jobscope_job_id = insert_or_update_job(
                job=job,
                company_id=company_id,
                location_id=location_id
            )

            # Link job to search
            add_job_to_search(
                search_id=search_id,
                jobscope_job_id=jobscope_job_id
            )

    finally:
        spark.stop()


if __name__ == "__main__":

    load_jobs(
        processed_path="s3a://jobscope-data/processed_data/2026-09-28/",
        role="Data Engineer",
        search_location="Coimbatore",
        country="India"
    )

    print("Jobs loaded successfully!")
