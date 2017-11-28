import boto3
import moto
import pytest
import dateutil
from collections import namedtuple

from ..state_storage import AdaptorStateStore, DatasetState


@pytest.fixture
def modified_date():
    return dateutil.parser.parse('2016-07-05T15:53:57.883+0000')


@pytest.fixture
def mock_dataset(modified_date):
    Dataset = namedtuple('Dataset',
                         ['uuid',
                          'modified_date',
                          'query_dataset_json',
                          'local_file_checksums'
                          ]
                         )
    return Dataset(
        'a_mock_uuid',
        modified_date,
        lambda x: 'A dataset title',
        {'a_file_name.zip', 'a_file_checksum'}
    )


@pytest.fixture
def dataset_state(mock_dataset):
    return DatasetState.create_from_dataset(mock_dataset)


class TestStateStore:

    def setup(self):
        self.mock = moto.mock_dynamodb2()
        self.mock.start()
        self.table_name = 'state_storage_test'

        self.ddb = boto3.resource('dynamodb')
        self.ddb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': 'uuid',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'uuid',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    def test_adaptor_state_store(self, dataset_state):
        state_store = AdaptorStateStore(self.table_name)
        state_store.put_dataset_state(dataset_state)
        store_dataset_state = state_store.get_dataset_state(dataset_state.uuid)
        assert dataset_state.json == store_dataset_state.json
        assert dataset_state == store_dataset_state

    def test_adaptor_state_store_latest(self, dataset_state, modified_date):
        state_store = AdaptorStateStore(self.table_name)
        state_store.update_latest_modified(dataset_state)
        latest_datetime = state_store.latest_modified_datetime()
        assert latest_datetime == modified_date

    def teardown(self):
        self.mock.stop()
