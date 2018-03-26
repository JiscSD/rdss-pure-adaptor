import os
from unittest.mock import (
    patch,
)

import boto3
from moto import (
    mock_s3,
    mock_dynamodb2,
)
import requests_mock

from ..pure_adaptor import (
    main,
)


@mock_s3
@mock_dynamodb2
def test_main_attempts_fetch_dataset_with_api_key():
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_client.create_table(
        TableName='mock-instance-id',
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        },
        KeySchema=[{
            'AttributeName': 'uuid',
            'KeyType': 'HASH',
        }],
        AttributeDefinitions=[],
    )

    mock_env = {
        'JISC_ID': '1234',
        'PURE_API_VERSION': 'v59',
        'PURE_API_URL': 'http://somewhere.over/the/rainbow',
        'PURE_API_KEY': 'secret-pure-key',
        'INSTANCE_ID': 'mock-instance-id',
        'RDSS_INTERNAL_INPUT_STREAM': 'mock-input-stream',
        'RDSS_MESSAGE_INVALID_STREAM': 'mock-invalid-stream',
        'RDSS_MESSAGE_ERROR_STREAM': 'mock-error-stream',
    }

    with patch.dict(os.environ, **mock_env), requests_mock.mock() as m:
        m.get('http://somewhere.over/the/rainbow/datasets', text='{}')
        m.head('http://somewhere.over/the/rainbow/datasets')
        main()

    assert m.last_request.headers['api-key'] == 'secret-pure-key'
