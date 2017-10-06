import boto3
import dateutil.parser


class AdaptorStateStore(object):
    LATEST_TAG = 'LATEST'

    def __init__(self, table_name):
        """ Initialises the AdaptorStateStore with the name of the dynamodb
            table used as a store.
        :table_name: String

        """
        dynamodb = boto3.resource(
            'dynamodb', endpoint_url='http://localhost:8000')
        self.table = dynamodb.Table(table_name)

    def latest_modified_date(self):
        """ Retrieves the datetime of the most recently modified dataset
            object from previous runs of the adaptor.
            :returns: DateTime
            """
        response = self.table.get_item(
            Key={'uuid': self.LATEST_TAG},
            ProjectionExpression='date_modified',
        )
        return dateutil.parser.parse(response.get('Item').get('date_modified'))

    def put_dataset_info(self, dataset_info):
        self.table.put_item(Item=dataset_info)

    def get_dataset_info(self, dataset_uuid):
        response = self.table.get_item(Key={'uuid': dataset_uuid})
        return response.get('Item')
