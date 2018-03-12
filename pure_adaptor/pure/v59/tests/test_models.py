import datetime
import json
import os
import pytest
import shutil

from ..models import PureDataset, ws_url_remap


class TestPureMessageMappings(object):

    def cleanup_taxonomy_dir(self):
        shutil.rmtree('temp_taxonomydata')

    @pytest.fixture(scope='module')
    def pure_json(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname,
                                'fixtures',
                                '2bdd031e-f373-424f-9657-192431ea4a06.json')
        with open(filename, 'r') as handle:
            contents = handle.read()
        return json.loads(contents)

    @pytest.fixture(scope='module')
    def pure_dataset(self, pure_json, request):
        request.addfinalizer(self.cleanup_taxonomy_dir)
        return PureDataset(pure_json)

    @pytest.fixture(scope='module')
    def person_role(self, pure_dataset):
        return pure_dataset.rdss_canonical_metadata['objectPersonRole'][0]

    def test_object_date(self, pure_dataset):
        date_value = '2017-05-16T15:50:27.337+0000'
        object_date = pure_dataset.rdss_canonical_metadata['objectDate'][0]
        assert object_date['dateValue'] == date_value

    def test_object_resourcetype(self, pure_dataset):
        res_type = pure_dataset.rdss_canonical_metadata['objectResourceType']
        assert res_type == 7

    def test_object_identifier(self, pure_dataset):
        obj_id = pure_dataset.rdss_canonical_metadata['objectIdentifier']
        id_value = 'http://dx.doi.org/10.5061/dryad.8638h'
        assert isinstance(obj_id, list)
        assert obj_id[0]['identifierValue'] == id_value

    def test_person_uuid(self, person_role):
        sample_uuid = 'ba8c1112-b6de-446b-ac2f-0b95c80a5cc2'
        assert person_role['person']['personUuid'] == sample_uuid

    def test_person_given_name(self, person_role):
        name = 'Alejandro  S\u00e1nchez-Amaro'
        assert person_role['person']['personGivenName'] == name

    def test_person_identifier(self, person_role):
        p_id = person_role['person']['personIdentifier'][0]
        assert p_id['personIdentifierValue'] == '250007106'
        assert p_id['personIdentifierType'] == 1

    def test_person_role(self, person_role):
        role_mapping = 5
        assert person_role['role'] == role_mapping

    def test_person_cn_sn(self, person_role):
        cn = 'Alejandro '
        sn = 'S\u00e1nchez-Amaro'
        assert person_role['person']['personCn'] == cn
        assert person_role['person']['personSn'] == sn

    def test_person_affiliation(self, person_role):
        assert person_role['person']['personAffiliation'][0] == 2

    def test_person_organisation_unit(self, pure_dataset):
        person_role = pure_dataset.rdss_canonical_metadata['object'
                                                           'PersonRole'][2]
        ou_uuid = 'e1dc1e3f-980e-4a49-8e46-b0ce898eccbb'
        ou_uname = 'School of Psychology and Neuroscience'
        person_ou = person_role['person']['personOrganisationUnit']
        assert person_ou['organisationUnitUuid'] == ou_uuid
        assert person_ou['organisationUnitName'] == ou_uname

    def test_obj_organisation_role(self, pure_dataset):
        org_role = pure_dataset.rdss_canonical_metadata['object'
                                                        'OrganisationRole']
        organisation = org_role['organisation']
        assert org_role['organisation']['organisationJiscId'] == 0
        assert organisation['organisationName'] == 'Dryad'
        assert organisation['organisationType'] == 8
        assert org_role['role'] == 9

    def test_obj_rights(self, pure_dataset):
        obj_rights = pure_dataset.rdss_canonical_metadata['objectRights'][0]
        licence = obj_rights['licence'][0]
        access = obj_rights['access'][0]
        assert obj_rights['rightsStatement'] == ''
        assert obj_rights['rightsHolder'] == ''
        assert licence['licenceName'] == 'CC BY'
        assert licence['licenceIdentifier'] == '/dk/atira/pure/dataset/'\
                                               'documentlicenses/cc-by'
        assert access['accessType'] == ''
        assert access['accessStatement'] == ''


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
