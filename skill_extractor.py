import re

from database.connection import get_connection


def normalize_text(text):
    text = text.lower()

    # Normalize common separators
    text = re.sub(r"[/_-]+", " ", text)

    # Keep + and # because of skills like C++ and C#
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_skills():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    skill_id,
                    skill_name,
                    normalized_name
                FROM skills;
            """)

            return cur.fetchall()

    finally:
        conn.close()


def get_jobs():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    jobscope_job_id,
                    description
                FROM jobs
                WHERE description IS NOT NULL;
            """)

            return cur.fetchall()

    finally:
        conn.close()


def extract_skills(description, skills):
    normalized_description = normalize_text(description)

    matched_skills = []

    for skill_id, skill_name, normalized_name in skills:

        # Match complete words/phrases rather than substrings
        pattern = rf"(?<!\w){re.escape(normalized_name)}(?!\w)"

        if re.search(pattern, normalized_description):
            matched_skills.append(skill_id)

    return matched_skills


def save_job_skills(job_skills):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            for jobscope_job_id, skill_id in job_skills:
                cur.execute("""
                    INSERT INTO job_skills (
                        jobscope_job_id,
                        skill_id
                    )
                    VALUES (%s, %s)
                    ON CONFLICT (
                        jobscope_job_id,
                        skill_id
                    )
                    DO NOTHING;
                """, (
                    jobscope_job_id,
                    skill_id
                ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def extract_all_job_skills():
    skills = get_skills()
    jobs = get_jobs()

    job_skills = []

    for jobscope_job_id, description in jobs:

        matched_skills = extract_skills(
            description,
            skills
        )

        for skill_id in matched_skills:
            job_skills.append(
                (
                    jobscope_job_id,
                    skill_id
                )
            )

        print(
            f"{jobscope_job_id}: "
            f"{len(matched_skills)} skills found"
        )

    save_job_skills(job_skills)

    print(
        f"\nInserted {len(job_skills)} job-skill relationships."
    )


if __name__ == "__main__":
    extract_all_job_skills()
