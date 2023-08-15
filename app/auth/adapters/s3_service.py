from typing import BinaryIO

import boto3
from urllib.parse import urlparse


class S3Service:
    def __init__(self):
        self.s3 = boto3.client("s3")

    def upload_media(self, file: BinaryIO, filename: str):
        bucket = "arthur.muratovich-bucket"
        filekey = f"avatars/{filename}"

        self.s3.upload_fileobj(file, bucket, filekey)

        bucket_location = boto3.client("s3").get_bucket_location(Bucket=bucket)
        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location["LocationConstraint"], bucket, filekey
        )

        return object_url

    def delete_avatar(self, file_url: str):
        parsed_url = urlparse(file_url)
        bucket = "arthur.muratovich-bucket"
        filekey = parsed_url.path.lstrip("/")
        print("filekey: ", filekey)

        s3 = boto3.client("s3")
        try:
            response = s3.delete_object(Bucket=bucket, Key=filekey)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 204:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    #     bucket_location = boto3.client("s3").get_bucket_location(Bucket=bucket)
    #     bucket = url_to_s3.netloc
    #     filekey = f"avatars/{filename}"

    #     # Delete the file from S3 bucket
    #     s3 = boto3.resource("s3")
    #     obj = s3.Object(bucket, filekey)
    #     obj.delete()

    #     return "File deleted from S3: " + url_to_s3

    #     return object_url
