import boto3

BUCKET_NAME = "jobscope-data"


def upload_file_to_s3(path):
    s3 = boto3.client("s3")

    try:
        s3.upload_file(
            path,
            BUCKET_NAME,
            path
        )
        print(f"Uploaded: s3://{BUCKET_NAME}/{path}")

    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        raise
