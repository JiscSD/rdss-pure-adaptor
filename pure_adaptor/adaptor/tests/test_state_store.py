import boto3
import copy
import moto
import pytest
import dateutil
from collections import namedtuple

from ..state_storage import AdaptorStateStore, DatasetState

MockMessage = namedtuple(
    'Message', [
        'as_json',
        'is_valid',
        'error_info'
    ]
)

MockDataset = namedtuple(
    'Dataset', [
        'pure_uuid',
        'modified_date',
        'rdss_canonical_metadata'
    ]
)


@pytest.fixture
def modified_date():
    return dateutil.parser.parse('2016-07-05T15:53:57.883+0000')


@pytest.fixture
def mock_dataset(modified_date):
    return MockDataset('a_mock_uuid', modified_date, {})


@pytest.fixture
def mock_valid_message():
    return MockMessage({'messageBody': {'objectTitle': 'Test Title'}}, True, ('', ''))


@pytest.fixture
def mock_invalid_message():
    return MockMessage({'messageBody': {}}, False, ('ERRORCODE', 'An error message'))


@pytest.fixture
def dataset_state(mock_dataset):
    return DatasetState.create_from_dataset(mock_dataset)


@moto.mock_dynamodb2
def setup_dynamodb_tables():
    watermark_table_name = 'watermark_table'
    processed_table_name = 'processed_table'
    ddb = boto3.resource('dynamodb')
    ddb.create_table(
        TableName=watermark_table_name,
        KeySchema=[{'AttributeName': 'Key', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'Key', 'AttributeType': 'S'}],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
    )
    ddb.create_table(
        TableName=processed_table_name,
        KeySchema=[{'AttributeName': 'Identifier', 'KeyType': 'HASH'}],
        AttributeDefinitions=[
            {'AttributeName': 'Identifier', 'AttributeType': 'S'}],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
    )
    return watermark_table_name, processed_table_name


@moto.mock_dynamodb2
def test_adaptor_state_store(dataset_state):
    state_store = AdaptorStateStore(*setup_dynamodb_tables())
    state_store.put_dataset_state(dataset_state)
    store_dataset_state = state_store.get_dataset_state(
        dataset_state.pure_uuid)
    assert dataset_state.json == store_dataset_state.json
    assert dataset_state == store_dataset_state


@moto.mock_dynamodb2
def test_adaptor_state_store_latest(modified_date):
    state_store = AdaptorStateStore(*setup_dynamodb_tables())
    state_store.update_high_watermark(modified_date.isoformat())
    latest_datetime = state_store.get_high_watermark()
    assert latest_datetime == modified_date


def test_dataset_update_with_message(dataset_state, mock_valid_message):
    original_state = copy.deepcopy(dataset_state)
    dataset_state.update_with_message(mock_valid_message)
    assert original_state != dataset_state


def test_dataset_state_success(dataset_state, mock_valid_message):
    dataset_state.update_with_message(mock_valid_message)
    assert dataset_state.json['Status'] == 'Success'
    assert dataset_state.json['Reason'] == ' - '


def test_dataset_state_invalid(dataset_state, mock_invalid_message):
    dataset_state.update_with_message(mock_invalid_message)
    assert dataset_state.json['Status'] == 'Invalid'
    assert dataset_state.json['Reason'] == 'ERRORCODE - An error message'
