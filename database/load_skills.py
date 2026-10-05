import pandas as pd

from connection import get_connection


INPUT_FILE = "../jobscope_skill_dictionary_normalized.csv"


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


if __name__ == "__main__":
    load_skills()
    print("Skills loaded successfully!")
