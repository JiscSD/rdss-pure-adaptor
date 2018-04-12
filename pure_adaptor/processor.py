import os
import logging
from .pure import versioned_pure_interface
from .pure.base import JMESCustomFunctions
from .adaptor.s3_bucket import BucketUploader
from .adaptor.kinesis_client import KinesisClient
from .adaptor.state_storage import AdaptorStateStore, DatasetState
from .adaptor.messages import MetadataCreate, MetadataUpdate

from rdsslib.taxonomy.taxonomy_client import TaxonomyGitClient


TAXONOMY_SCHEMA_REPO = 'https://github.com/JiscRDSS/taxonomyschema.git'
GIT_TAG = 'v0.1.0'
logger = logging.getLogger(__name__)


class PureAdaptor(object):

    def __init__(self,
                 api_version,
                 api_url,
                 api_key,
                 instance_id,
                 input_stream,
                 invalid_stream,
                 error_stream,
                 pure_flow_limit):

        self.instance_id = instance_id
        self.api_version = api_version
        self.pure = versioned_pure_interface(api_version)
        self.pure_flow_limit = pure_flow_limit

        try:
            self.state_store = AdaptorStateStore(instance_id)
            self.upload_manager = BucketUploader(instance_id)
            self.kinesis_client = KinesisClient(input_stream,
                                                invalid_stream,
                                                error_stream)
            self.pure_api = self.pure.API(api_url, api_key)
        except Exception:
            logging.exception('PureAdaptor Initialisation failed.')

    def _poll_for_changed_datasets(self):
        """ Scrape the API for datasets that have changed since the last time
            the adaptor was run.
            :returns: [PureDataset]
            """
        latest_datetime = self.state_store.latest_modified_datetime()
        changed_datasets = self.pure_api.changed_datasets(latest_datetime)
        changed_datasets.sort(key=lambda ds: ds.modified_date)
        return changed_datasets

    def _process_dataset(self, dataset, temp_dir_path):
        """ Undertakes the processing of a single dataset, managing all data
            download and upload, as well as sending messages to the appropriate
            stream.
            :dataset: PureDataset
            :returns: DatasetState
            """

        dataset.download_files(temp_dir_path)
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
            s3_url = self.upload_manager.upload_file(dataset.doi_upload_key,
                                                     file_path)
            dataset.file_s3_urls[os.path.basename(file_path)] = s3_url

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
        self.state_store.put_dataset_state(latest_dataset_state)
        self.state_store.update_latest_modified(latest_dataset_state)

    def run(self, temp_dir_path):
        """ Runs the adaptor.
            """
        taxonomy_client = TaxonomyGitClient(TAXONOMY_SCHEMA_REPO, GIT_TAG,
                                            temp_dir_path)
        custom_mapping_funcs = JMESCustomFunctions(taxonomy_client)
        changed_datasets = self._poll_for_changed_datasets()

        if not changed_datasets:
            logger.info(
                'No new datasets available from %s, exiting.', self.pure_api)

        else:
            for dataset in changed_datasets[:self.pure_flow_limit]:
                dataset.custom_funcs = custom_mapping_funcs
                self._process_dataset(dataset, temp_dir_path)
