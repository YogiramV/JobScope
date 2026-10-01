from connection import get_connection


def get_jobs():
    # Get all jobs

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT
                            *
                        FROM
                            jobs
                        """)
            jobs = cur.fetchall()

            return jobs

    except:
        print("Connection failed")

    finally:
        conn.close()


def get_jobs_by_role(role):
    # Get jobs by given role

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT
                            *
                        FROM
                            jobs
                        WHERE
                            title ILIKE %s
                        """, (f"%{role}%",))
            jobs = cur.fetchall()

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_jobs_by_location(location):
    # Get jobs by given location

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 
                            j.*
                        FROM 
                            jobs j
                        JOIN 
                            locations l
                        ON 
                            j.location_id = l.location_id
                        WHERE 
                            l.location_name ILIKE %s
                        """, (f"%{location}%",))
            jobs = cur.fetchall()

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_job_counts_by_location(location):
    # Get total jobs in a location

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 
                            COUNT(j.*)
                        FROM 
                            jobs j
                        JOIN 
                            locations l
                        ON 
                            j.location_id = l.location_id
                        WHERE 
                            l.location_name ILIKE %s
                        """, (f"%{location}%",))
            jobs = cur.fetchone()[0]

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_job_counts_grouped_by_location(location):
    # Get job distribution in a location

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 
                            l.location_name,COUNT(j.*)
                        FROM 
                            jobs j
                        JOIN 
                            locations l
                        ON 
                            j.location_id = l.location_id
                        WHERE 
                            l.location_name ILIKE %s
                        GROUP BY
                            l.location_name
                        ORDER BY
                            COUNT(j.*) DESC
                        """, (f"%{location}%",))
            jobs = cur.fetchall()

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_job_counts_by_role(role):
    # Get total jobs by role

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 
                            title,COUNT(*)
                        FROM 
                            jobs
                        WHERE
                            title ILIKE %s
                        GROUP BY
                            title
                        """, (f"%{role}%",))
            jobs = cur.fetchall()

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_job_counts_by_company():
    # Get total jobs in companies

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 
                            c.company_name,COUNT(*)
                        FROM 
                            jobs j
                        JOIN
                            companies c
                        ON
                            j.company_id=c.company_id
                        GROUP BY
                            c.company_name
                        ORDER BY
                            COUNT(*) DESC
                        """)
            jobs = cur.fetchall()

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_job_counts_grouped_by_company(company):
    # Get total jobs in a given company

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 
                            title,COUNT(*)
                        FROM 
                            jobs j
                        JOIN
                            companies c
                        ON
                            j.company_id=c.company_id
                        WHERE
                            c.company_name ILIKE %s
                        GROUP BY
                            title
                        ORDER BY
                            COUNT(*) DESC
                        """, (f"%{company}%",))
            jobs = cur.fetchall()

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_job_counts_by_employment_type(employment_type):
    # Get total jobs by given employment type

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 
                            COUNT(*)
                        FROM 
                            jobs 
                        WHERE
                            employment_type ILIKE %s
                        """, (f"%{employment_type}%",))
            jobs = cur.fetchone()[0]

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_job_counts_grouped_by_employment_type():
    # Get total jobs by employment type

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT 
                            employment_type,COUNT(*)
                        FROM 
                            jobs 
                        GROUP BY
                            employment_type
                        ORDER BY
                            COUNT(*) DESC
                        """)
            jobs = cur.fetchall()

            return jobs

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_salary_statistics():
    # Get salary statistics

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT
                            AVG(annual_salary_min),
                            AVG(annual_salary_max),
                            MIN(annual_salary_min),
                            MAX(annual_salary_max),
                            COUNT(*)
                        FROM
                            jobs
                        WHERE
                            annual_salary_min IS NOT NULL
                            OR annual_salary_max IS NOT NULL
                        """)
            salary_statistics = cur.fetchone()

            return salary_statistics
            # [Avg min,Avg Max, Min,Max]

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_salary_by_role(role):
    # Get salary by role

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT
                            title,
                            AVG(annual_salary_min),
                            AVG(annual_salary_max)
                        FROM
                            jobs
                        WHERE
                            title ILIKE %s
                            AND (
                                annual_salary_min IS NOT NULL
                                OR annual_salary_max IS NOT NULL
                            )
                        GROUP BY
                            title
                        ORDER BY
                            AVG(annual_salary_max) DESC
                        """, (f"%{role}%",))
            salary_data = cur.fetchall()

            return salary_data
            # [Title,Min. Salary, Max. Salary]

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_salary_by_location():
    # Get salary by locations

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT
                            l.location_name,
                            AVG(j.annual_salary_min),
                            AVG(j.annual_salary_max)
                        FROM
                            jobs j
                        JOIN
                            locations l
                        ON
                            j.location_id = l.location_id
                        WHERE
                            j.annual_salary_min IS NOT NULL
                            OR j.annual_salary_max IS NOT NULL
                        GROUP BY
                            l.location_name
                        ORDER BY
                            AVG(j.annual_salary_max) DESC
                        """)
            salary_data = cur.fetchall()

            return salary_data
            # [location,min salary,max salary]

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def get_monthly_job_counts():
    # Get job posting trends

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT
                            DATE_TRUNC('month', first_seen_at) AS month,
                            COUNT(*)
                        FROM
                            jobs
                        GROUP BY
                            month
                        ORDER BY
                            month
                        """)
            monthly_jobs = cur.fetchall()

            return monthly_jobs
            # [Month,Count]

    except Exception as e:
        print(f"Database error: {e}")

    finally:
        conn.close()
