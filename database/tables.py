from connection import get_connection


def create_tables():
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # Companies table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    company_id BIGSERIAL PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Locations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    location_id BIGSERIAL PRIMARY KEY,
                    city VARCHAR(100),
                    state VARCHAR(100),
                    country VARCHAR(100) NOT NULL,
                    location_name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (city, state, country)
                );
            """)

            # Search configurations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS search_configurations (
                    search_id BIGSERIAL PRIMARY KEY,
                    role VARCHAR(255) NOT NULL,
                    location VARCHAR(255) NOT NULL,
                    country VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    UNIQUE (role, location, country)
                );
            """)

            # Jobs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    jobscope_job_id VARCHAR(64) PRIMARY KEY,
                    job_id TEXT NOT NULL UNIQUE,
                    title VARCHAR(255) NOT NULL,
                    company_id BIGINT NOT NULL,
                    location_id BIGINT NOT NULL,
                    description TEXT NOT NULL,
                    via VARCHAR(255),
                    source_link TEXT,
                    apply_options JSONB,
                    employment_type VARCHAR(100),
                    annual_salary_min NUMERIC(12, 2),
                    annual_salary_max NUMERIC(12, 2),
                    first_seen_at TIMESTAMP NOT NULL,
                    last_seen_at TIMESTAMP NOT NULL,

                    FOREIGN KEY (company_id)
                        REFERENCES companies(company_id),

                    FOREIGN KEY (location_id)
                        REFERENCES locations(location_id),

                    CHECK (
                        annual_salary_min IS NULL
                        OR annual_salary_max IS NULL
                        OR annual_salary_min <= annual_salary_max
                    )
                );
            """)

            # Job searches table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS job_searches (
                    search_id BIGINT NOT NULL,
                    jobscope_job_id VARCHAR(64) NOT NULL,
                    discovered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    PRIMARY KEY (search_id, jobscope_job_id),

                    FOREIGN KEY (search_id)
                        REFERENCES search_configurations(search_id),

                    FOREIGN KEY (jobscope_job_id)
                        REFERENCES jobs(jobscope_job_id)
                );
            """)

            # Skills table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    skill_id BIGSERIAL PRIMARY KEY,
                    skill_name VARCHAR(100) NOT NULL UNIQUE,
                    normalized_name VARCHAR(150) NOT NULL UNIQUE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Job-Skills relationship table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS job_skills (
                    jobscope_job_id VARCHAR(64) NOT NULL,
                    skill_id BIGINT NOT NULL,

                    PRIMARY KEY (jobscope_job_id, skill_id),

                    FOREIGN KEY (jobscope_job_id)
                        REFERENCES jobs(jobscope_job_id)
                        ON DELETE CASCADE,

                    FOREIGN KEY (skill_id)
                        REFERENCES skills(skill_id)
                        ON DELETE CASCADE
                );
            """)

            # Indexes
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_company_id
                ON jobs(company_id);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_location_id
                ON jobs(location_id);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_employment_type
                ON jobs(employment_type);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_salary_min
                ON jobs(annual_salary_min);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_salary_max
                ON jobs(annual_salary_max);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_title
                ON jobs(title);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_job_searches_job_id
                ON job_searches(jobscope_job_id);
            """)

            cur.execute(""" 
                CREATE INDEX IF NOT EXISTS idx_job_skills_skill_id
                ON job_skills(skill_id);
            """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def drop_tables():
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                DROP TABLE IF EXISTS job_searches;
            """)

            cur.execute("""
                DROP TABLE IF EXISTS job_skills;
            """)

            cur.execute("""
                DROP TABLE IF EXISTS skills;
            """)

            cur.execute("""
                DROP TABLE IF EXISTS jobs;
            """)

            cur.execute("""
                DROP TABLE IF EXISTS search_configurations;
            """)

            cur.execute("""
                DROP TABLE IF EXISTS locations;
            """)

            cur.execute("""
                DROP TABLE IF EXISTS companies;
            """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
    print("Tables created!")
