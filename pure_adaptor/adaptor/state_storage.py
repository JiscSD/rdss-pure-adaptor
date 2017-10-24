import boto3
import logging
import dateutil.parser

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AdaptorStateStore(object):
    LATEST_TAG = 'LATEST'

    def __init__(self, table_name):
        """ Initialises the AdaptorStateStore with the name of the dynamodb
            table used as a store.
            :table_name: String
            """
        try:
            dynamodb = boto3.resource('dynamodb')
            self.table = dynamodb.Table(table_name)
            self.table.load()
            logging.info('Successfully initialised connection to '
                         'AdaptorStateStore %s', self.table.name)
        except ClientError as e:
            logging.error('AdaptorStateStore initialisation: %s', e)
            raise

    def put_dataset_state(self, dataset_state):
        """ Attempts to put a DatasetState into the AdaptorStateStore.
            Overwrites any existing DatasetState with the same UUID in the
            store.
            :dataset_state: DatasetState
            """
        try:
            logging.info('Putting DatasetState for %s into AdaptorStateStore.',
                         dataset_state.uuid)
            self.table.put_item(Item=dataset_state.json)
        except ClientError as e:
            logging.error('AdaptorStateStore put_dataset_state failure: %s', e)

    def get_dataset_state(self, dataset_uuid):
        """ Attempts to retrieve by UUID the state of a dataset from the
            AdaptorStateStore. If a matching dataset is not found an
            empty DatasetState is returned.
            :dataset_uuid: String
            :returns: DatasetState
            """
        try:
            logging.info('Getting DatasetState for %s from AdaptorStateStore.',
                         dataset_uuid)
            response = self.table.get_item(Key={'uuid': dataset_uuid})
            item = response.get('Item', {})
            return DatasetState(item)
        except ClientError as e:
            logging.error('AdaptorStateStore get_dataset_state failure: %s', e)

    def latest_modified_datetime(self):
        """ Retrieves the datetime of the most recently modified dataset
            object from previous runs of the adaptor.
            :returns: DateTime
            """
        try:
            logging.info(
                'Retrieving latest_modified_datetime from AdaptorStateStore.')
            response = self.table.get_item(
                Key={'uuid': self.LATEST_TAG},
                ProjectionExpression='date_modified',
            )
            date_string = response.get('Item', {}).get('date_modified')
            if date_string:
                return dateutil.parser.parse(date_string)
            else:
                return None
        except ClientError as e:
            logging.error('AdaptorStateStore latest_modified_datetime \
                    failure: %s', e)

    def update_latest(self, dataset_state):
        """ Sets the provided DatasetState as the most recently modified dataset
            in the state store.
            :dataset_state: DatasetState
            """
        dataset_state.json['uuid'] = self.LATEST_TAG
        self.put_dataset_state(dataset_state)


class DatasetState(object):

    def __init__(self, state_json):
        """ Initialise a StoredDatasetData object with the response from the
            dynamodb AdaptorStateStore.
            """
        self.json = state_json

    @property
    def uuid(self):
        return self.json['uuid']

    @classmethod
    def create_from_dataset(cls, dataset):
        """ Initialise a StoredDatasetData object with a PureDataset object.
            """
        dataset_json = {
            'uuid': dataset.uuid,
            'date_modified': dataset.modified_date.isoformat(),
            'watched_fields': {
                'title': dataset.query_dataset_json('title[0].value'),
                'files': dataset.local_file_checksums,
            }
        }
        return cls(dataset_json)

    @property
    def watched_fields(self):
        """ Extract and return a dict of the fields being watched in datasets.
            Used as the basis of comparison for whether a dataset re-appearing
            in the API should trigger a CREATE or UPDATE message.
            :return: dict
            """
        return self.json.get('watched_fields', {})

    def __eq__(self, other):
        return (self.watched_fields == other.watched_fields)

    def __ne__(self, other):
        return (self.watched_fields != other.watched_fields)
