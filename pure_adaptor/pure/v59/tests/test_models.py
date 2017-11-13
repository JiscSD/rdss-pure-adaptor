import datetime

from ..models import PureDataset, ws_url_remap


class TestPureDataset():

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
                'modifiedDate': self.now.isoformat()
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
