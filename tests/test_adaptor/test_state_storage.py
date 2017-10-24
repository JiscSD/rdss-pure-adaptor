import boto3
import moto
import pytest

from pure_adaptor.adaptor.state_storage import AdaptorStateStore


@pytest.fixture
def dynamodb_table_name():
    return 'local_pure_adaptor_test'


@moto.mock_dynamodb2
@pytest.fixture
def state_store():
    return AdaptorStateStore(dynamodb_table_name)


@moto.mock_dynamodb2
@pytest.fixture
def dynamodb_state_store_table():
    ddb = boto3.resource('dynamodb')
    ddb.create_table(
        TableName=dynamodb_table_name,
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


def test_adaptor_state_store_latest(state_store):

    pass
