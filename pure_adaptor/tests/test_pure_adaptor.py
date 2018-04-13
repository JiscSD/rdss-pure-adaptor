import json
import os
import re
from unittest.mock import (
    patch,
)

import boto3
from moto import (
    mock_s3,
    mock_dynamodb2,
    mock_kms,
    mock_kinesis,
    mock_ssm,
)
import requests_mock

from ..pure_adaptor import (
    main,
)


def _setup_mock_environment():
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

    s3_client = boto3.client('s3', region_name='eu-west-2')
    s3_client.create_bucket(Bucket='mock-instance-id')

    kinesis_client = boto3.client('kinesis', region_name='eu-west-2')
    kinesis_client.create_stream(
        StreamName='mock-input-stream',
        ShardCount=1
    )
    kinesis_client.create_stream(
        StreamName='mock-invalid-stream',
        ShardCount=1
    )
    kinesis_client.create_stream(
        StreamName='mock-error-stream',
        ShardCount=1
    )

    return {
        'JISC_ID': '1234',
        'HEI_ADDRESS': '4 Privet Drive',
        'PURE_API_VERSION': 'v59',
        'PURE_API_URL': 'http://somewhere.over/the/rainbow',
        'PURE_API_KEY_SSM_PARAMETER_NAME': 'x-marks-the-spot',
        'INSTANCE_ID': 'mock-instance-id',
        'RDSS_INTERNAL_INPUT_STREAM': 'mock-input-stream',
        'RDSS_MESSAGE_INVALID_STREAM': 'mock-invalid-stream',
        'RDSS_MESSAGE_ERROR_STREAM': 'mock-error-stream',
        'PURE_FLOW_LIMIT':  '60'
    }


def _get_records(client, stream_name):
    shard_id = client.describe_stream(
        StreamName=stream_name,
    )['StreamDescription']['Shards'][0]['ShardId']
    shard_iterator = client.get_shard_iterator(
        StreamName=stream_name,
        ShardId=shard_id,
        ShardIteratorType='TRIM_HORIZON',
    )['ShardIterator']
    result = client.get_records(
        ShardIterator=shard_iterator,
        Limit=1000,
    )
    return result['Records']


@mock_s3
@mock_dynamodb2
@mock_kms
@mock_kinesis
@mock_ssm
def test_main_attempts_fetch_dataset_with_api_key():
    env = _setup_mock_environment()

    with patch.dict(os.environ, **env), requests_mock.mock() as m:
        m.get('http://somewhere.over/the/rainbow/datasets', text='{}')
        m.head('http://somewhere.over/the/rainbow/datasets')
        main()

    assert m.last_request.headers['api-key'] == 'secret-pure-key'


@mock_s3
@mock_dynamodb2
@mock_kms
@mock_kinesis
@mock_ssm
def test_uuids_added_to_data():
    env = _setup_mock_environment()

    pure_item_filename = os.path.join(
        os.path.dirname(__file__), '..', 'pure', 'v59', 'tests', 'fixtures',
        '2bdd031e-f373-424f-9657-192431ea4a06.json')
    with open(pure_item_filename, 'rb') as pure_item_file:
        pure_item = json.loads(pure_item_file.read())

    response = json.dumps({
        'items': [pure_item]
    })

    with patch.dict(os.environ, **env), requests_mock.mock() as m:
        m.get('http://riswebtest.st-andrews.ac.uk/portal/'
              'files/241900740/Supporting_Data.zip', text='')
        m.get('http://somewhere.over/the/rainbow/datasets', text=response)
        m.head('http://somewhere.over/the/rainbow/datasets')
        main()

    kinesis_client = boto3.client('kinesis', region_name='eu-west-2')

    record = _get_records(kinesis_client, 'mock-input-stream')[0]

    uuid4hex = re.compile(
        '^[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}$', re.I)
    body = json.loads(record['Data'])['messageBody']

    objectUuid = body['objectUuid']
    person = body['objectPersonRole'][0]['person']
    personUuid = person['personUuid']
    orgUuid = person['personOrganisationUnit']['organisationUnitUuid']
    relatedUuid = body['objectRelatedIdentifier'][0]['identifierValue']
    fileUuid = body['objectFile'][0]['fileUuid']
    storageUuid = body['objectFile'][0]['fileStoragePlatform']['storagePlatformUuid']

    assert uuid4hex.match(objectUuid)
    assert uuid4hex.match(personUuid)
    assert uuid4hex.match(orgUuid)
    assert uuid4hex.match(relatedUuid)
    assert uuid4hex.match(fileUuid)
    assert uuid4hex.match(storageUuid)
    assert len(set([objectUuid, personUuid, orgUuid,
                    relatedUuid, fileUuid, storageUuid])) == 6


@mock_s3
@mock_dynamodb2
@mock_kms
@mock_kinesis
@mock_ssm
def test_if_no_document_license_not_sent_to_error_or_invalid():
    env = _setup_mock_environment()

    pure_item_filename = os.path.join(
        os.path.dirname(__file__), '..', 'pure', 'v59', 'tests', 'fixtures',
        'no-document-licenses.json')
    with open(pure_item_filename, 'rb') as pure_item_file:
        pure_item = json.loads(pure_item_file.read())

    response = json.dumps({
        'items': [pure_item]
    })

    with patch.dict(os.environ, **env), requests_mock.mock() as m:
        m.get('http://riswebtest.st-andrews.ac.uk/portal/'
              'files/241900740/Supporting_Data.zip', text='')
        m.get('http://somewhere.over/the/rainbow/datasets', text=response)
        m.head('http://somewhere.over/the/rainbow/datasets')
        main()

    kinesis_client = boto3.client('kinesis', region_name='eu-west-2')

    error_records = _get_records(kinesis_client, 'mock-error-stream')
    invalid_records = _get_records(kinesis_client, 'mock-error-stream')
    assert len(error_records) == 0
    assert len(invalid_records) == 0


@mock_s3
@mock_dynamodb2
@mock_kms
@mock_kinesis
@mock_ssm
def test_if_multiple_documents_not_sent_to_error():
    env = _setup_mock_environment()

    pure_item_filename = os.path.join(
        os.path.dirname(__file__), '..', 'pure', 'v59', 'tests', 'fixtures',
        'multiple-documents.json')
    with open(pure_item_filename, 'rb') as pure_item_file:
        pure_item = json.loads(pure_item_file.read())

    response = json.dumps({
        'items': [pure_item]
    })

    with patch.dict(os.environ, **env), requests_mock.mock() as m:
        m.get('http://riswebtest.st-andrews.ac.uk/portal/'
              'files/241900740/Supporting_Data.zip', text='')
        m.get('http://somewhere.over/the/rainbow/datasets', text=response)
        m.head('http://somewhere.over/the/rainbow/datasets')
        main()

    kinesis_client = boto3.client('kinesis', region_name='eu-west-2')

    error_records = _get_records(kinesis_client, 'mock-error-stream')
    invalid_records = _get_records(kinesis_client, 'mock-error-stream')
    assert len(error_records) == 0
    assert len(invalid_records) == 0
