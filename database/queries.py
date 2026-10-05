from connection import get_connection
from psycopg2.extras import Json


def get_or_create_location(city, state, country):
    location_name = f"{city}, {state}"
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO locations (
                    city,
                    state,
                    country,
                    location_name
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (city, state, country)
                DO UPDATE SET location_name = EXCLUDED.location_name
                RETURNING location_id;
            """, (
                city,
                state,
                country,
                location_name
            ))

            location_id = cur.fetchone()[0]

        conn.commit()

        return location_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_or_create_company(company_name):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                    INSERT INTO companies (
                        company_name
                    )
                    VALUES (%s)
                    ON CONFLICT (company_name)
                    DO UPDATE SET company_name = EXCLUDED.company_name
                    RETURNING company_id;
                """, (
                company_name,
            ))

            company_id = cur.fetchone()[0]

        conn.commit()

        return company_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_or_create_search_configuration(role, location, country):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO search_configurations (
                    role,
                    location,
                    country
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (role, location, country)
                DO UPDATE SET role = EXCLUDED.role
                RETURNING search_id;
            """, (
                role,
                location,
                country
            ))

            search_id = cur.fetchone()[0]

        conn.commit()

        return search_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def insert_or_update_job(job, company_id, location_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO jobs (
                    jobscope_job_id,
                    job_id, title,
                    company_id, location_id,
                    description, via,
                    source_link,
                    apply_options,
                    employment_type,
                    annual_salary_min,
                    annual_salary_max,
                    first_seen_at,
                    last_seen_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                ON CONFLICT (jobscope_job_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    company_id = EXCLUDED.company_id,
                    location_id = EXCLUDED.location_id,
                    description = EXCLUDED.description,
                    via = EXCLUDED.via,
                    source_link = EXCLUDED.source_link,
                    apply_options = EXCLUDED.apply_options,
                    employment_type = EXCLUDED.employment_type,
                    annual_salary_min = EXCLUDED.annual_salary_min,
                    annual_salary_max = EXCLUDED.annual_salary_max,
                    last_seen_at = CURRENT_TIMESTAMP
                RETURNING jobscope_job_id;
            """, (
                job["jobscope_job_id"],
                job["job_id"],
                job["title"],
                company_id,
                location_id,
                job["description"],
                job["via"],
                job["source_link"],
                Json(job["apply_options"]),
                job["employment_type"],
                job["annual_salary_min"],
                job["annual_salary_max"]
            ))

            jobscope_job_id = cur.fetchone()[0]

        conn.commit()

        return jobscope_job_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def add_job_to_search(search_id, jobscope_job_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                    INSERT INTO job_searches (
                        search_id,
                        jobscope_job_id
                    )
                    VALUES (%s, %s)
                    ON CONFLICT (search_id, jobscope_job_id)
                    DO NOTHING
                    RETURNING search_id, jobscope_job_id;
                """, (
                search_id,
                jobscope_job_id
            ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
