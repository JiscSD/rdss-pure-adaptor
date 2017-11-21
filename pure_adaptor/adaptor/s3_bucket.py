import boto3
import os
import json
import io
import urllib
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BucketUploader(object):

    def __init__(self, bucket_name, top_level_prefix=None):
        """ Initialises a BucketUploader instance with the name of the bucket
            being uploaded to, ensuring that the bucket is accessible.
            :bucket_name: String
            :top_level_prefix: String
            """
        self._bucket_name = bucket_name
        self._top_level_prefix = top_level_prefix
        try:
            s3 = boto3.resource('s3')
            self.bucket = s3.Bucket(self._bucket_name)
            self.bucket.load()
            logging.info('Successfully initialised connection to '
                         's3 bucket %s', self.bucket.name)
        except ClientError as e:
            logging.exception('s3 Bucket initialisation: %s', e)

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

    def _s3_url(self, key):
        """ Builds and returns an s3 url for the provided key in this
            bucket, using the "s3://" scheme.
            """
        url_tuple = ('s3', self._bucket_name, key, '', '')
        return urllib.parse.urlunsplit(url_tuple)

    def upload_file(self, prefix, source_file):
        """ Attempts to upload the provided file to the s3 bucket.
            """
        key = self._build_key(prefix, source_file)
        logger.info('Uploading %s to %s.', source_file, key)
        with open(source_file, 'rb') as data:
            self.bucket.upload_fileobj(data, key)
        return self._s3_url(key)

    def upload_json_obj(self, prefix, file_name, json_obj):
        """ Attempts to upload a json object to the s3 bucket.
            """
        key = self._build_key(prefix, file_name)
        logger.info('Uploading json object to %s.', key)
        json_data = io.BytesIO(json.dumps(json_obj, indent=2).encode('utf-8'))
        self.bucket.upload_fileobj(json_data, key)
        return self._s3_url(key)
