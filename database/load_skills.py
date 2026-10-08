from dotenv import load_dotenv
from connection import get_connection
import pandas as pd
import os


load_dotenv()


# ============================================================
# Configuration
# ============================================================

JOB_SCOPE_PATH = os.getenv(
    "JOB_SCOPE_PATH",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

INPUT_FILE = os.path.join(
    JOB_SCOPE_PATH,
    "resources",
    "jobscope_skill_dictionary_normalized.csv"
)


# ============================================================
# Load Skills
# ============================================================

def load_skills():

    df = pd.read_csv(INPUT_FILE)

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            for _, row in df.iterrows():

                cur.execute("""
                    INSERT INTO skills (
                        skill_name,
                        normalized_name
                    )
                    VALUES (%s, %s)
                    ON CONFLICT (skill_name)
                    DO NOTHING;
                """, (
                    row["skill_name"],
                    row["normalized_name"],
                ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    load_skills()
    print("Skills loaded successfully!")
