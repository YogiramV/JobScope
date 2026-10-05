import boto3

BUCKET_NAME = "jobscope-data"


def upload_file_to_s3(local_path, s3_key):
    s3 = boto3.client("s3")

    try:
        s3.upload_file(local_path, BUCKET_NAME, s3_key)
        print(f"Uploaded: s3://{BUCKET_NAME}/{s3_key}")

    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        raise
