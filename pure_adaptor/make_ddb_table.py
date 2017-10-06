import boto3

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

table = ddb.create_table(
    TableName='local_pure_test',
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
