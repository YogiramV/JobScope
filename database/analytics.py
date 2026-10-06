import pandas as pd
from database.connection import get_connection

# ============================================================
# Job Explorer
# ============================================================


def get_jobs():
    """Return jobs for the Job Explorer."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    j.title,
                    c.company_name,
                    l.location_name,
                    j.employment_type,
                    j.annual_salary_min,
                    j.annual_salary_max,
                    j.via,
                    j.source_link
                FROM jobs j
                JOIN companies c
                    ON j.company_id = c.company_id
                JOIN locations l
                    ON j.location_id = l.location_id
                ORDER BY j.last_seen_at DESC;
            """)

            rows = cur.fetchall()

            columns = [
                "Title",
                "Company",
                "Location",
                "Employment Type",
                "Salary Min",
                "Salary Max",
                "Via",
                "Source",
            ]

            jobs = pd.DataFrame(rows, columns=columns)

            jobs["Salary"] = jobs.apply(
                _format_salary,
                axis=1,
            )

            return jobs

    finally:
        conn.close()


def _format_salary(row):
    """Format salary values for dashboard display."""

    minimum = row["Salary Min"]
    maximum = row["Salary Max"]

    if pd.isna(minimum) and pd.isna(maximum):
        return "Not disclosed"

    if pd.notna(minimum) and pd.notna(maximum):
        return f"₹{minimum:,.0f} – ₹{maximum:,.0f}"

    if pd.notna(minimum):
        return f"₹{minimum:,.0f}+"

    return f"Up to ₹{maximum:,.0f}"


# ============================================================
# Overview
# ============================================================

def get_overview_metrics():
    """Return high-level JobScope metrics."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total_jobs,
                    COUNT(DISTINCT company_id) AS total_companies,
                    COUNT(DISTINCT location_id) AS total_locations,
                    COUNT(*) FILTER (
                        WHERE annual_salary_min IS NOT NULL
                           OR annual_salary_max IS NOT NULL
                    ) AS jobs_with_salary
                FROM jobs;
            """)

            return cur.fetchone()

    finally:
        conn.close()


def get_jobs_grouped_by_location():
    """Return job counts grouped by location."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    l.location_name,
                    COUNT(j.jobscope_job_id) AS job_count
                FROM jobs j
                JOIN locations l
                    ON j.location_id = l.location_id
                GROUP BY
                    l.location_id,
                    l.location_name
                ORDER BY
                    job_count DESC;
            """)

            return cur.fetchall()

    finally:
        conn.close()


def get_job_counts_grouped_by_employment_type():
    """Return job counts grouped by employment type."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    employment_type,
                    COUNT(*) AS job_count
                FROM jobs
                GROUP BY employment_type
                ORDER BY job_count DESC;
            """)

            return cur.fetchall()

    finally:
        conn.close()


def get_salary_availability():
    """Return the number of jobs with and without salary information."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    CASE
                        WHEN annual_salary_min IS NOT NULL
                          OR annual_salary_max IS NOT NULL
                        THEN 'Salary Available'
                        ELSE 'Salary Not Available'
                    END AS salary_status,
                    COUNT(*) AS job_count
                FROM jobs
                GROUP BY salary_status
                ORDER BY salary_status;
            """)

            return cur.fetchall()

    finally:
        conn.close()


# ============================================================
# Job Market
# ============================================================

def get_jobs_grouped_by_title():
    """Return job counts grouped by job title."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    title,
                    COUNT(*) AS job_count
                FROM jobs
                GROUP BY title
                ORDER BY job_count DESC;
            """)

            return cur.fetchall()

    finally:
        conn.close()


def get_job_counts_by_company():
    """Return job counts grouped by company."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.company_name,
                    COUNT(*) AS job_count
                FROM jobs j
                JOIN companies c
                    ON j.company_id = c.company_id
                GROUP BY c.company_name
                ORDER BY job_count DESC;
            """)

            return cur.fetchall()

    finally:
        conn.close()


def get_jobs_by_selected_location(location):
    """Return job-title counts for a selected location."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    j.title,
                    COUNT(*) AS job_count
                FROM jobs j
                JOIN locations l
                    ON j.location_id = l.location_id
                WHERE l.location_name ILIKE %s
                GROUP BY j.title
                ORDER BY job_count DESC;
            """, (f"%{location}%",))

            return cur.fetchall()

    finally:
        conn.close()


def get_jobs_by_employment_type(employment_type):
    """Return job-title counts for a selected employment type."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    title,
                    COUNT(*) AS job_count
                FROM jobs
                WHERE employment_type ILIKE %s
                GROUP BY title
                ORDER BY job_count DESC;
            """, (f"%{employment_type}%",))

            return cur.fetchall()

    finally:
        conn.close()


# ============================================================
# Salary
# ============================================================

def get_salary_by_role(role):
    """Return average salary range for a selected role."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    title,
                    AVG(annual_salary_min) AS average_salary_min,
                    AVG(annual_salary_max) AS average_salary_max
                FROM jobs
                WHERE
                    title ILIKE %s
                    AND (
                        annual_salary_min IS NOT NULL
                        OR annual_salary_max IS NOT NULL
                    )
                GROUP BY title
                ORDER BY average_salary_max DESC;
            """, (f"%{role}%",))

            return cur.fetchall()

    finally:
        conn.close()


def get_salary_by_location():
    """Return average salary range grouped by location."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    l.location_name,
                    AVG(j.annual_salary_min) AS average_salary_min,
                    AVG(j.annual_salary_max) AS average_salary_max
                FROM jobs j
                JOIN locations l
                    ON j.location_id = l.location_id
                WHERE
                    j.annual_salary_min IS NOT NULL
                    OR j.annual_salary_max IS NOT NULL
                GROUP BY l.location_name
                ORDER BY average_salary_max DESC;
            """)

            return cur.fetchall()

    finally:
        conn.close()


# ============================================================
# Skills
# ============================================================

def get_skill_demand():
    """Return the top 10 most demanded skills."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    s.skill_name,
                    COUNT(*) AS skill_count
                FROM job_skills js
                JOIN skills s
                    ON js.skill_id = s.skill_id
                GROUP BY
                    s.skill_id,
                    s.skill_name
                ORDER BY
                    skill_count DESC
                LIMIT 10;
            """)

            return cur.fetchall()

    finally:
        conn.close()


def get_skills_by_role(role):
    """Return skill demand for a selected role."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    s.skill_name,
                    COUNT(DISTINCT js.jobscope_job_id) AS job_count
                FROM job_skills js
                JOIN skills s
                    ON js.skill_id = s.skill_id
                JOIN jobs j
                    ON js.jobscope_job_id = j.jobscope_job_id
                WHERE j.title ILIKE %s
                GROUP BY
                    s.skill_id,
                    s.skill_name
                ORDER BY
                    job_count DESC;
            """, (f"%{role}%",))

            return cur.fetchall()

    finally:
        conn.close()


def get_skills_by_location(location):
    """Return skill demand for a selected location."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    s.skill_name,
                    COUNT(DISTINCT js.jobscope_job_id) AS job_count
                FROM job_skills js
                JOIN skills s
                    ON js.skill_id = s.skill_id
                JOIN jobs j
                    ON js.jobscope_job_id = j.jobscope_job_id
                JOIN locations l
                    ON j.location_id = l.location_id
                WHERE l.location_name ILIKE %s
                GROUP BY
                    s.skill_id,
                    s.skill_name
                ORDER BY
                    job_count DESC;
            """, (f"%{location}%",))

            return cur.fetchall()

    finally:
        conn.close()


def get_skill_combinations():
    """Return the top 10 skill combinations."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    s1.skill_name || ' + ' || s2.skill_name
                        AS skill_combination,
                    COUNT(DISTINCT js1.jobscope_job_id) AS job_count
                FROM job_skills js1
                JOIN job_skills js2
                    ON js1.jobscope_job_id = js2.jobscope_job_id
                    AND js1.skill_id < js2.skill_id
                JOIN skills s1
                    ON js1.skill_id = s1.skill_id
                JOIN skills s2
                    ON js2.skill_id = s2.skill_id
                GROUP BY
                    s1.skill_id,
                    s1.skill_name,
                    s2.skill_id,
                    s2.skill_name
                ORDER BY
                    job_count DESC
                LIMIT 10;
            """)

            return cur.fetchall()

    finally:
        conn.close()
