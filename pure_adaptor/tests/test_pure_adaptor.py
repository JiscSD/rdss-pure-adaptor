import os
from unittest.mock import (
    patch,
)

import boto3
from moto import (
    mock_s3,
    mock_dynamodb2,
    mock_kms,
    mock_ssm,
)
import requests_mock

from ..pure_adaptor import (
    main,
)


@mock_s3
@mock_dynamodb2
@mock_kms
@mock_ssm
def test_main_attempts_fetch_dataset_with_api_key():
    kms_client = boto3.client('kms', region_name='eu-west-2')
    kms_key_id = kms_client.create_key()['KeyMetadata']['KeyId']
    ssm_client = boto3.client('ssm', region_name='eu-west-2')
    ssm_client.put_parameter(
        Name='x-marks-the-spot',
        Value='secret-pure-key',
        Type='SecureString',
        KeyId=kms_key_id,
    )

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
        'PURE_API_KEY_SSM_PARAMETER_NAME': 'x-marks-the-spot',
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
