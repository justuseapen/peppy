import boto3
from botocore.exceptions import ClientError
from flask import current_app
import logging

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
    )

def upload_file_to_s3(file, filename):
    s3_client = get_s3_client()
    try:
        s3_client.upload_fileobj(
            file,
            current_app.config['S3_BUCKET'],
            filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
    except ClientError as e:
        logging.error(e)
        return None
    return f"{current_app.config['S3_LOCATION']}{filename}"

def delete_file_from_s3(filename):
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(Bucket=current_app.config['S3_BUCKET'], Key=filename)
    except ClientError as e:
        logging.error(e)
        return False
    return True
