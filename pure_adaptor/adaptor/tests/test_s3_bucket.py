import boto3
import moto
import pytest
import tempfile
import json
import os
import io

from ..s3_bucket import BucketUploader


@pytest.fixture
def test_file_path():
    return os.path.join(os.path.dirname(__file__), 'fixtures/test_file.txt')


@pytest.fixture
def test_file_md5():
    """ MD5 of fixture/test_file.txt generated with
        `openssl md5 -binary ./test_file.txt | base64`
        """
    return 'xs+A2UIwvGrnurn86AHVZg=='


@pytest.fixture
def test_json_obj():
    return {'a': {'test': ['JSON', 'object']}}


class TestBucketUploader(object):

    def setup(self):
        self.mock = moto.mock_s3()
        self.mock.start()
        self.bucket_name = 'a_test_bucket'
        self.test_prefix = 'a/test/prefix'
        self.s3_client = boto3.client('s3')
        self.s3_client.create_bucket(Bucket=self.bucket_name)

    def test_file_upload(self, test_file_path, test_file_md5):
        uploader = BucketUploader(self.bucket_name)
        uploader.upload_file(self.test_prefix, test_file_path, test_file_md5)

        _, file_name = os.path.split(test_file_path)
        tmp_dir = tempfile.TemporaryDirectory()
        download_path = os.path.join(tmp_dir.name, file_name)

        self.s3_client.download_file(
            self.bucket_name,
            os.path.join(self.test_prefix, file_name),
            download_path)
        with open(download_path, 'r') as dl_in:
            dl_data = dl_in.read()
        with open(test_file_path, 'r') as orig_in:
            orig_data = orig_in.read()

        assert dl_data == orig_data

    def test_json_obj_upload(self, test_json_obj):
        uploader = BucketUploader(self.bucket_name)
        test_json_obj_name = 'test_obj.json'
        uploader.upload_json_obj(self.test_prefix,
                                 test_json_obj_name,
                                 test_json_obj
                                 )
        s3_obj = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=os.path.join(self.test_prefix, test_json_obj_name)
        )
        with io.BytesIO(s3_obj['Body'].read()) as buff:
            json_obj = json.load(buff)

        assert json_obj == test_json_obj

    def teardown(self):
        self.mock.stop()
