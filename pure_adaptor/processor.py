import logging
from pure import versioned_pure_interface
from adaptor.s3_bucket import BucketUploader
from adaptor.checksum import ChecksumGenerator
from adaptor.state_storage import AdaptorStateStore, DatasetState

logger = logging.getLogger(__name__)


class PureAdaptor(object):

    def __init__(self, api_version, api_url, api_key, s3_bucket):
        self.instance_info = '{}'.format(api_version)
        self.pure = versioned_pure_interface(api_version)
        self.pure_api = pure.API(api_url, api_key)
        self.state_store = AdaptorStateStore(environment)
        self.upload_manager = BucketUploader(upload_bucket, bucket_prefix)
        self.checksum_gen = DatasetHasher()

    def _poll_for_changed_datasets():
        """ Scrape the API for datasets that have changed since the last time
            the adaptor was run.
            :returns: [PureDataset]
            """
        latest_date = self.state_store.latest_modified_date()
        changed_datasets = pure_api.changed_datasets(last_datetime)
        changed_datasets.sort(key=lambda ds: ds.modified_date)
        return changed_datasets

    def _process_dataset(dataset):
        """ Undertakes the processing of a single dataset, managing all data
            download and upload, as well as sending messages to the appropriate
            stream.
            :dataset: PureDataset
            :returns: DatasetState
            """

        dataset.download_files()
        dataset.local_file_checksums = self.checksum_gen.file_checksums(
            dataset)
        self._upload_dataset(dataset)
        dataset_state = StoredDatasetData.create_from_dataset(dataset)
        prev_dataset_state = state_store.get_dataset_state(dataset.uuid)

        if dataset_state == prev_dataset_state:
            # UPDATE
            print('UPDATE')

        else:
            # CREATE
            print('CREATE')

        return dataset_state

    def _upload_dataset(dataset):
        """ Effects the upload of dataset files and associated metadata to the
            appropriate S3 bucket for retrieval by other RDSS components.
            :dataset: PureDataset
            """
        for file_path in dataset.local_files:
            self.upload_manager.upload_file(dataset.doi_upload_key, file_path)

        self.upload_manager.upload_json_obj(
            dataset.doi_upload_key,
            'original_pure{}_metadata.json'.format(self.instance_info),
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

    def run():

        changed_datasets = self._poll_for_changed_datasets()

        if not changed_datasets:
            logger.info(
                'No new datasets available from {}, exiting.', self.pure_api)

        else:
            for dataset in changed_datasets:
                latest_dataset_state = self._process_dataset(dataset)

        self._update_adaptor_state(latest_dataset_state)
