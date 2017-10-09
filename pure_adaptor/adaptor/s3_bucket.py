import boto3
import os
import json
import io
import logging

logger = logging.getLogger(__name__)


class BucketUploader(object):

    def __init__(self, bucket_name, top_level_prefix=None, profile=None):
        self._bucket_name = bucket_name
        self._top_level_prefix = top_level_prefix
        self._profile = profile or None
        self._bucket = None

    def _build_key(self, prefix, file_name):
        """ Builds a full key for file upload to the s3 bucket, using the
            uploader's additional top_level_prefix if provided.
            :prefix: String
            :file_name: String
            :returns: String
            """
        if self._top_level_prefix:
            return os.path.join(
                self._top_level_prefix,
                prefix,
                os.path.basename(file_name)
            )
        else:
            return os.path.join(
                prefix,
                os.path.basename(file_name)
            )

    @property
    def bucket(self):
        if not self._bucket:
            session = boto3.Session(profile_name=self._profile)
            s3 = session.resource('s3')
            self._bucket = s3.Bucket(self._bucket_name)
        return self._bucket

    def upload_file(self, prefix, source_file):
        """ Attempts to upload the provided file to the s3 bucket.
            """
        key = self._build_key(prefix, source_file)
        with open(source_file, 'rb') as data:
            self.bucket.upload_fileobj(data, key)

    def upload_json_obj(self, prefix, file_name, json_obj):
        """ Attempts to upload a json object to the s3 bucket.
            """
        key = self._build_key(prefix, file_name)
        json_data = io.BytesIO(json.dumps(json_obj, indent=2).encode('utf-8'))
        self.bucket.upload_fileobj(json_data, key)
