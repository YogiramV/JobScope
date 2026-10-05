import os
import json
import datetime
from s3 import upload_file_to_s3

import serpapi
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("SERPAPI_API_KEY")

RAW_DATA = "/home/yogi/workspace/DataScience/Projects/JobScope/raw_data"


def fetch_jobs(role, location):
    try:
        client = serpapi.Client(api_key=API_KEY)
        results = client.search({
            "engine": "google_jobs",
            "q": role,
            "location": location,
            "google_domain": "google.co.in",
            "hl": "en",
            "gl": "in"
        })
    except Exception as e:
        print(f"Error fetching jobs from API: {e}")
        raise

    return dict(results)


def save_response(role, location, results):
    today = str(datetime.date.today())

    todays_dir = RAW_DATA + "/" + today

    filename = (
        role + "_" + location.split(",")[0].strip()
    ).lower().replace(" ", "_") + ".json"

    os.makedirs(todays_dir, exist_ok=True)

    local_path = todays_dir + "/" + filename
    s3_key = "raw_data/" + today + "/" + filename

    with open(local_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    upload_file_to_s3(local_path, s3_key)


def load_sample(role, location):
    todays_dir = RAW_DATA + "/" + str(datetime.date.today())

    filename = (
        role + "_" + location.split(",")[0].strip()
    ).lower().replace(" ", "_") + ".json"

    try:
        with open(
            todays_dir + "/" + filename,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except FileNotFoundError:
        print("File doesn't exist.")
        raise


def get_jobs(role, location):
    results = fetch_jobs(role, location)

    save_response(role, location, results)

    print("Fresh data fetched and saved.")

    jobs = results.get("jobs_results", [])

    return jobs


def get_sample_jobs(role, location):
    results = load_sample(role, location)

    print("Using saved sample data.")

    jobs = results.get("jobs_results", [])

    return jobs
