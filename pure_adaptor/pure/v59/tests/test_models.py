import datetime
import json
import os
import pytest

from ..models import PureDataset, ws_url_remap


class TestPureMessageMappings(object):

    @pytest.fixture
    def pure_json(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname,
                                'fixtures',
                                '2bdd031e-f373-424f-9657-192431ea4a06.json')
        with open(filename, 'r') as handle:
            contents = handle.read()
        return json.loads(contents)

    @pytest.fixture
    def pure_dataset(self, pure_json):
        return PureDataset(pure_json)

    def test_object_date(self, pure_dataset):
        date_value = '2017-05-16T15:50:27.337+0000'
        object_date = pure_dataset.rdss_canonical_metadata['objectDate'][0]
        assert object_date['dateValue'] == date_value

    def test_object_resourcetype(self, pure_dataset):
        res_type = pure_dataset.rdss_canonical_metadata['objectResourceType']
        assert res_type == 7

    def test_person_uuid(self, pure_dataset):
        sample_uuid = 'ba8c1112-b6de-446b-ac2f-0b95c80a5cc2'
        person = pure_dataset.rdss_canonical_metadata['objectPersonRole'][0]
        assert person['person']['personUuid'] == sample_uuid


class TestPureDataset(object):

    def setup(self):
        self.now = datetime.datetime.now(datetime.timezone.utc)
        self.uuid = 'a_test_uuid'
        self.doi = 'a/test/doi'
        self.url_name_pairs = [
            ('https://pure_endpoint_url.ac.uk/ws/files/an_id/'
             'test_dataset_file_one.txt',
             'test_dataset_file_one.txt'),
            ('https://pure_endpoint_url.ac.uk/ws/files/an_id/'
             'test_dataset_file_two.txt',
             'test_dataset_file_two.txt')]

        self.mock_dataset = {
            'uuid': self.uuid,
            'doi': self.doi,
            'info': {
                'modifiedDate': self.now.isoformat(),
                'modifiedBy': 'testuser'
            },
            'documents': [{'title': n, 'url': u}
                          for u, n in self.url_name_pairs]
        }

        self.pure_dataset = PureDataset(self.mock_dataset)

    def test_uuid(self):
        assert self.pure_dataset.uuid == self.uuid

    def test_modified_date(self):
        assert self.pure_dataset.modified_date == self.now

    def test_files(self):
        assert self.pure_dataset.files == [
            (ws_url_remap(u), n) for u, n in self.url_name_pairs]

    def test_original_metadata(self):
        assert self.pure_dataset.original_metadata == self.mock_dataset

    def test_doi_key(self):
        assert self.pure_dataset.doi_upload_key == self.doi

    def test_no_doi_key(self):
        no_doi_ds = self.mock_dataset
        no_doi_ds['doi'] = ''
        no_doi_pds = PureDataset(no_doi_ds)
        assert no_doi_pds.doi_upload_key == 'no_doi/{}'.format(self.uuid)

    def teardown(self):
        pass


def test_ws_url_remap():
    url = 'https://pure_endpoint_url.ac.uk/ws/files/an_id/test_file.pdf'
    url_map = 'http://pure_endpoint_url.ac.uk/portal/files/an_id/test_file.pdf'
    assert ws_url_remap(url) == url_map
