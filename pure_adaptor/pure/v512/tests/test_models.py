import datetime
import json
import os
import pytest
import shutil
import tempfile
import mock

from ..models import PureDataset
from pure_adaptor.pure.base import JMESCustomFunctions

from rdsslib.taxonomy.taxonomy_client import TaxonomyGitClient
TAXONOMY_SCHEMA_REPO = 'https://github.com/JiscRDSS/taxonomyschema.git'
GIT_TAG = 'v0.1.0'


class TestPureMessageMappings(object):

    def cleanup_taxonomy_dir(self, dirpath):
        shutil.rmtree(dirpath)

    def _load_pure_json_response_item(self, file_name):
        path = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            file_name
        )
        with open(path, 'r') as f_in:
            pure_response = json.load(f_in)
        return pure_response['items'][0]

    @pytest.fixture
    def remapping_funcs(self):
        tempdir = tempfile.mkdtemp()
        yield JMESCustomFunctions(
            TaxonomyGitClient(TAXONOMY_SCHEMA_REPO, GIT_TAG, tempdir)
        )
        self.cleanup_taxonomy_dir(tempdir)

    @pytest.fixture
    @mock.patch.dict(os.environ,
                     {'PURE_API_URL': 'https://an_institution.with_pure.ac.uk/ws/api/512/',
                      'JISC_ID': '99999',
                      'HEI_ADDRESS': 'An address'})
    def first_dataset(self, remapping_funcs):
        pure_json = self._load_pure_json_response_item(
            'pure_512_api_response_0.json')
        dataset = PureDataset(pure_json)
        dataset.custom_funcs = remapping_funcs
        return dataset.rdss_canonical_metadata

    @pytest.fixture
    @mock.patch.dict(os.environ,
                     {'PURE_API_URL': 'https://an_institution.with_pure.ac.uk/ws/api/512/',
                      'JISC_ID': '99999',
                      'HEI_ADDRESS': 'An address'})
    def second_dataset(self, remapping_funcs):
        pure_json = self._load_pure_json_response_item(
            'pure_512_api_response_1.json')
        dataset = PureDataset(pure_json)
        dataset.custom_funcs = remapping_funcs
        return dataset.rdss_canonical_metadata

    def test_object_date(self, first_dataset, second_dataset):
        first_value = '2016-01-15T13:00:06.023+0000'
        first_date = first_dataset['objectDate'][0]
        second_date = second_dataset['objectDate'][0]
        second_value = '2016-03-28T09:32:48.911+0000'
        assert first_date['dateValue'] == first_value
        assert second_date['dateValue'] == second_value

    def test_object_resourcetype(self, first_dataset, second_dataset):
        assert first_dataset['objectResourceType'] == 7
        assert second_dataset['objectResourceType'] == 7

    def test_object_identifier(self, first_dataset, second_dataset):
        first_obj_ids = first_dataset['objectIdentifier']
        second_obj_ids = second_dataset['objectIdentifier']

        first_url_value = 'https://an_institution.with_pure.ac.uk/ws/'\
            'api/512/datasets/59e932cf-3a34-4b7b-bf08-f12a3a2c7273'
        first_doi_value = '10.001100/b5698935-7651-4333-b00e-2ed2e072eb6a'

        second_url_value = 'https://an_institution.with_pure.ac.uk/ws/'\
            'api/512/datasets/ac2c0adf-163d-4a27-b975-f2fa9f46d974'
        assert isinstance(first_obj_ids, list)
        assert len(first_obj_ids) == 2
        assert first_obj_ids[0]['identifierValue'] == first_url_value
        assert first_obj_ids[1]['identifierValue'] == first_doi_value

        assert isinstance(second_obj_ids, list)
        assert len(second_obj_ids) == 1
        assert second_obj_ids[0]['identifierValue'] == second_url_value

    def test_object_related_identifiers(self, first_dataset, second_dataset):
        first_obj_rel_ids = first_dataset['objectRelatedIdentifier']
        second_obj_rel_ids = second_dataset['objectRelatedIdentifier']
        assert len(first_obj_rel_ids) == 1
        assert first_obj_rel_ids[0]['identifier']['identifierType'] == 18
        assert first_obj_rel_ids[0]['identifier']['identifierValue'] == \
            'https://an_institution.with_pure.ac.uk/ws/' \
            'api/512/projects/95d44235-ffab-4260-b9bb-65dd5d2d0fa2'
        assert first_obj_rel_ids[0]['relationType'] == 11

        assert len(second_obj_rel_ids) == 3
        assert second_obj_rel_ids[0]['identifier']['identifierType'] == 18
        assert second_obj_rel_ids[0]['identifier']['identifierValue'] == \
            'https://an_institution.with_pure.ac.uk/ws/' \
            'api/512/projects/44ca6661-b4d6-410d-b071-b91c79c352a9'
        assert second_obj_rel_ids[0]['relationType'] == 11

        assert second_obj_rel_ids[1]['identifier']['identifierType'] == 18
        assert second_obj_rel_ids[1]['identifier']['identifierValue'] == \
            'https://an_institution.with_pure.ac.uk/ws/' \
            'api/512/research-outputs/lk83ed12-191e-425d-a072-c5ee0b7811ed'
        assert second_obj_rel_ids[1]['relationType'] == 14

    def test_object_person_role(self, first_dataset, second_dataset):
        first_person_role = first_dataset['objectPersonRole'][0]
        second_person_roles_1 = second_dataset['objectPersonRole'][0]
        second_person_roles_2 = second_dataset['objectPersonRole'][2]
        assert first_person_role['role'] == 5
        assert first_person_role['person']['personGivenNames'] == 'Solange'
        assert first_person_role['person']['personFamilyNames'] == 'Knowles'

        assert second_person_roles_1['role'] == 5
        assert second_person_roles_1['person']['personGivenNames'] == 'Mark E.'
        assert second_person_roles_1['person']['personFamilyNames'] == 'Smith'

        assert second_person_roles_2['role'] == 5
        assert second_person_roles_2['person']['personGivenNames'] == 'Marc'
        assert second_person_roles_2['person']['personFamilyNames'] == 'Riley'

    def test_person_organisation_unit(self, second_dataset):
        person = second_dataset['objectPersonRole'][0]['person']

        assert person['personOrganisationUnit']['organisationUnitUuid']\
            == '42aabe6a-5b0e-4776-a2bd-90c0849be6e7'
        assert person['personOrganisationUnit']['organisationUnitName']\
            == 'The Fall'

    def test_obj_organisation_role(self, first_dataset):
        first_org_role = first_dataset['objectOrganisationRole'][0]
        assert first_org_role['organisation']['organisationJiscId'] == 99999
        assert first_org_role['organisation']['organisationName'] == 'Terrible Records'
        assert first_org_role['organisation']['organisationType'] == 9
        assert first_org_role['role'] == 5

    def test_obj_rights(self, first_dataset, second_dataset):
        first_obj_rights = first_dataset['objectRights']
        second_obj_rights = second_dataset['objectRights']
        assert first_obj_rights['licence'][0]['licenceName'] == 'not present'
        assert first_obj_rights['licence'][0]['licenceIdentifier'] == 'not present'
        assert first_obj_rights['access'][0]['accessType'] == 1
        assert first_obj_rights['access'][0]['accessStatement'] == 'not present'

        assert second_obj_rights['licence'][0]['licenceName'] == 'CC BY'
        assert second_obj_rights['licence'][0]['licenceIdentifier']\
            == '/dk/atira/pure/dataset/documentlicenses/cc-by'
        assert second_obj_rights['access'][0]['accessType'] == 1
        assert second_obj_rights['access'][0]['accessStatement'] == 'not present'


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

    def test_pure_uuid(self):
        assert self.pure_dataset.pure_uuid == self.uuid

    def test_modified_date(self):
        assert self.pure_dataset.modified_date == self.now

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
