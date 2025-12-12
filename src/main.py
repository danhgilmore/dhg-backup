#!/usr/bin/env python3
import io
import os

import configparser
import boto3
from boto3.s3.transfer import S3UploadFailedError

# s3_client = boto3.client(s3,
#                          aws_access_key_id=aws_access_key_id,
#                          aws_secret_access_key=aws_secret_access_key,
#                          region_name=region)


def do_scenario(s3_resource):
    print("Testing S3 Connection...")

    config = configparser.ConfigParser()
    config.read('../docs/config.ini')

    aws_access_key_id = config['AWS']['aws_access_key_id']
    aws_secret_access_key = config['AWS']['aws_secret_access_key']
    region = config['AWS']['region']
    output_format = config['AWS']['output_format']
    bucket_name = config['AWS']['bucket_name']

    bucket = s3_resource.Bucket(bucket_name)
    print(f"Connected to bucket: {bucket.name}")

    file_name = None
    while file_name is None:
        file_name = input("\nEnter the file name to upload: ").strip()
        if not os.path.isfile(file_name):
            print(f"File '{file_name}' does not exist.")
            file_name = None
            return

    obj = bucket.Object(os.path.basename(file_name))
    try:
        obj.upload_file(file_name)
        print(
            f"Uploaded file '{file_name}' to bucket '{bucket.name}' as object '{obj.key}'")
    except S3UploadFailedError as e:
        print(f"Failed to upload file: {e}")
        return


if __name__ == "__main__":
    do_scenario(boto3.resource("s3"))
