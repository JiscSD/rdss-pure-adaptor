import boto3
import logging
import datetime
import dateutil.parser

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AdaptorStateStore(object):
    HIGH_WATERMARK_KEY = 'HighWatermark'

    def __init__(self, watermark_table_name, processed_table_name):
        """ Initialises the AdaptorStateStore with the name of the dynamodb
            tables used to store the high watermark of the adaptor, and the
            set of records that have already been processed.
            :watermark_table_name: String
            :processed_table_name: String
            """
        self.watermark_table = self._init_dynamodb_table(watermark_table_name)
        self.processed_table = self._init_dynamodb_table(processed_table_name)

    def _init_dynamodb_table(self, table_name):
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(table_name)
            table.load()
            logging.info('Successfully initialised connection to '
                         '%s', table_name)
            return table
        except ClientError:
            logging.exception('%s initialisation failed.', table_name)

    def put_dataset_state(self, dataset_state):
        """ Attempts to put a DatasetState into the AdaptorStateStore.
            Overwrites any existing DatasetState with the same id in the
            store.
            :dataset_state: DatasetState
            """
        try:
            logging.info('Putting DatasetState for %s into %s.',
                         dataset_state.pure_uuid, self.processed_table.name)
            self.processed_table.put_item(Item=dataset_state.json)
        except ClientError:
            logging.exception('Unable to put %s into %s.',
                              dataset_state.json, self.processed_table.name)

    def get_dataset_state(self, pure_identifier):
        """ Attempts to retrieve by pure_identifier the state of a dataset from the
            AdaptorStateStore. If a matching dataset is not found an
            empty DatasetState is returned.
            :pure_identifier: String
            :returns: DatasetState
            """
        try:
            logging.info('Getting DatasetState for %s from %s.',
                         pure_identifier, self.processed_table.name)
            response = self.processed_table.get_item(
                Key={'Identifier': pure_identifier})
            item = response.get('Item', {})
            return DatasetState(item)
        except ClientError:
            logging.exception('Unable to get DatasetState for %s from %s.',
                              pure_identifier, self.processed_table.name)

    def get_high_watermark(self):
        """ Retrieves the datetime of the most recently modified dataset
            object from previous runs of the adaptor.
            :returns: DateTime
            """
        try:
            logging.info(
                'Retrieving high watermark from %s.', self.watermark_table.name)
            response = self.watermark_table.get_item(
                Key={'Key': self.HIGH_WATERMARK_KEY})
            date_string = response.get('Item', {}).get('Value')
            if date_string:
                return dateutil.parser.parse(date_string)
            else:
                return None
        except ClientError:
            logging.exception(
                'Unable to get a high watermark from %s.', self.watermark_table.name)

    def update_high_watermark(self, high_watermark_datetime):
        """ Sets the provided Date time string as the high watermark in the state store.
            :high_watermark_datetime: String
            """
        try:
            logging.info('Setting high watermark as %s',
                         high_watermark_datetime)
            self.watermark_table.put_item(Item={
                'Key': self.HIGH_WATERMARK_KEY,
                'Value': high_watermark_datetime,
                'LastUpdated': datetime.datetime.now().isoformat()
            })
        except ClientError:
            logging.exception('Unable to put %s into %s.',
                              high_watermark_datetime, self.watermark_table.name)


class DatasetState(object):

    def __init__(self, state_json):
        """ Initialise a StoredDatasetData object with the response from the
            dynamodb AdaptorStateStore.
            """
        self.json = state_json

    @property
    def pure_uuid(self):
        return self.json['Identifier']

    @property
    def last_updated(self):
        return self.json['LastUpdated']

    @classmethod
    def create_from_dataset(cls, dataset):
        """ Initialise a StoredDatasetData object with a PureDataset object.
            Creates a dummy messageBody for comparison.
            """
        dataset_json = {
            'Identifier': dataset.pure_uuid,
            'LastUpdated': dataset.modified_date.isoformat(),
            'Message': {
                'messageBody': dataset.rdss_canonical_metadata
            },
        }
        return cls(dataset_json)

    def update_with_message(self, message):
        self.json.update({
            'Message': message.as_json,
            'Status': 'Success' if message.is_valid else 'Invalid',
            'Reason': ' - '.join(message.error_info)
        })

    @property
    def message_body(self):
        """ Extract and return the messageBody from the last generated message for this dataset.
            Used to determine whether the modification of the dataset in Pure has changed the
            RDSS CDM manifestation of a dataset and whether an UPDATE message should be generated.
            If no messageBody then will return None to indicate a CREATE message should be
            generated.
            :return: dict
            """
        return self.json.get('Message', {}).get('messageBody')

    @property
    def object_uuid(self):
        """ Extract and return the objectUUID from the stored message.
            Used to effect object versioning as defined in the message api spec."""
        return self.json.get('Message', {}).get('messageBody', {}).get('objectUuid')

    def __eq__(self, other):
        return (self.message_body == other.message_body)

    def __ne__(self, other):
        return (self.message_body != other.message_body)
