import logging
from pure import versioned_pure_interface
from adaptor.s3_bucket import BucketUploader
from adaptor.kinesis_client import KinesisClient
from adaptor.state_storage import AdaptorStateStore, DatasetState
from adaptor.messages import MetadataCreate, MetadataUpdate

logger = logging.getLogger(__name__)


class PureAdaptor(object):

    def __init__(self,
                 api_version,
                 api_url,
                 api_key,
                 instance_id,
                 input_queue,
                 invalid_queue,
                 error_queue):

        self.instance_id = instance_id
        self.api_version = api_version
        self.kinesis_client = KinesisClient(input_queue,
                                            invalid_queue,
                                            error_queue)
        self.pure = versioned_pure_interface(api_version)
        self.pure_api = self.pure.API(api_url, api_key)
        self.state_store = AdaptorStateStore(instance_id)
        self.upload_manager = BucketUploader(instance_id)

    def _poll_for_changed_datasets(self):
        """ Scrape the API for datasets that have changed since the last time
            the adaptor was run.
            :returns: [PureDataset]
            """
        latest_datetime = self.state_store.latest_modified_datetime()
        changed_datasets = self.pure_api.changed_datasets(latest_datetime)
        changed_datasets.sort(key=lambda ds: ds.modified_date)
        return changed_datasets

    def _process_dataset(self, dataset):
        """ Undertakes the processing of a single dataset, managing all data
            download and upload, as well as sending messages to the appropriate
            stream.
            :dataset: PureDataset
            :returns: DatasetState
            """

        dataset.download_files()
        self._upload_dataset(dataset)
        dataset_state = DatasetState.create_from_dataset(dataset)
        prev_dataset_state = self.state_store.get_dataset_state(dataset.uuid)

        if dataset_state == prev_dataset_state:
            message_creator = MetadataUpdate(self.instance_id)
        else:
            message_creator = MetadataCreate(self.instance_id)

        message = message_creator.generate(dataset.rdss_canonical_metadata)

        self.kinesis_client.put_record(message)

        self._update_adaptor_state(dataset_state)

    def _upload_dataset(self, dataset):
        """ Effects the upload of dataset files and associated metadata to the
            appropriate S3 bucket for retrieval by other RDSS components.
            :dataset: PureDataset
            """
        for file_path in dataset.local_files:
            self.upload_manager.upload_file(dataset.doi_upload_key, file_path)

        self.upload_manager.upload_json_obj(
            dataset.doi_upload_key,
            'original_pure{}_metadata.json'.format(self.api_version),
            dataset.original_metadata
        )
        self.upload_manager.upload_json_obj(
            dataset.doi_upload_key,
            'metadata.json',
            dataset.rdss_canonical_metadata
        )

    def _update_adaptor_state(self, latest_dataset_state):
        """ Updates the state store with the latest datetime from the set
            of datasets downloaded during this run of the adaptor.
            :latest_dataset_state: DatasetState
            """
        self.state_store.update_latest(latest_dataset_state)

    def run(self):
        """ Runs the adaptor.
            """

        changed_datasets = self._poll_for_changed_datasets()

        if not changed_datasets:
            logger.info(
                'No new datasets available from %s, exiting.', self.pure_api)

        else:
            # For the sake of testing atm, I'm limiting this to 20 at a time.
            for dataset in changed_datasets[:20]:
                self._process_dataset(dataset)
