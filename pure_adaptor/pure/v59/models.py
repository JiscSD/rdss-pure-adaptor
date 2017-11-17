import os
import dateutil.parser
import urllib
import jmespath
import logging
from ..base import BasePureDataset
from ..base import JSONRemapper

from .download_manager import PureDownloadManager
from .checksum import ChecksumGenerator

logger = logging.getLogger(__name__)

pure_to_canonical_mapper = JSONRemapper(
    os.path.join(os.path.dirname(__file__), 'research_object_mapping.txt'))
checksum_generator = ChecksumGenerator()


def ws_url_remap(pure_data_url):
    """ Modifies a data location url to be http and /portal rather than /ws
        Required for at least the test instance of the PURE API from
        St. Andrews.
        """
    url_parts = list(urllib.parse.urlsplit(pure_data_url))
    path_parts = [p for p in url_parts[2].split('/') if p]
    url_parts[2] = '/'.join(['portal'] + path_parts[1:])
    url_parts[0] = 'http'
    return urllib.parse.urlunsplit(url_parts)


def file_name_from_url(url):
    return os.path.basename(urllib.parse.urlsplit(url)[2])


class PureDataset(BasePureDataset):
    """Abstraction around the dataset responses from the Pure API.
        """

    def __init__(self, dataset_json, pure_api_instance=None):
        """ Initialises the dataset with the dataset json object returned
            from the Pure API
            """
        if pure_api_instance:
            self._download_manager = PureDownloadManager(pure_api_instance)
        self._dataset_json = dataset_json
        self.local_files = []
        self.local_file_checksums = {}
        self.file_s3_urls = {}

    def __str__(self):
        return 'PureDataset: {}'.format(self.uuid)

    def query_dataset_json(self, query):
        return jmespath.search(query, self._dataset_json)

    def _file_info(self, file_json):
        """ Extracts the url and file name for a file.
            """
        file_name = file_json.get('title')
        url = ws_url_remap(file_json.get('url'))
        return url, file_name

    def _format_checksum(self, file_name):
        return [{
            'checksumType': 2,  # sha256
            'checksumValue': self.local_file_checksums.get(file_name)
        }]

    def _format_local_data(self, obj_file):
        file_name = file_name_from_url(obj_file['fileIdentifier'])
        obj_file['fileChecksum'] = self._format_checksum(file_name)
        obj_file['fileStorageLocation'] = self.file_s3_urls.get(file_name)
        obj_file['fileStorageType'] = 0  # s3
        obj_file['fileStorageStatus'] = 0  # online
        obj_file['fileUploadStatus'] = 1  # uploadComplete
        return obj_file

    def _update_with_local_data(self, canonical_metadata):
        """ Updates fields in the canonical data model with data that
            has been generated locally and was not available through
            the Pure API.
            """
        object_files = canonical_metadata.get('objectFile')
        if not object_files:
            return canonical_metadata
        else:
            new_object_files = []
            for obj_file in object_files:
                new_obj_file = self._format_local_data(obj_file)
                new_object_files.append(new_obj_file)
            canonical_metadata['objectFile'] = new_object_files
            return canonical_metadata

    @property
    def doi_upload_key(self):
        doi_key = self._dataset_json.get('doi')
        if not doi_key:
            alternate_key = self._dataset_json.get('uuid')
            doi_key = 'no_doi/{}'.format(alternate_key)
        return doi_key.strip()

    @property
    def original_metadata(self):
        return self._dataset_json

    @property
    def rdss_canonical_metadata(self):
        logger.info('Remapping pure dataset %s to canonical metadata.',
                    self.uuid)
        metadata = pure_to_canonical_mapper.remap(self._dataset_json)
        return self._update_with_local_data(metadata)

    @property
    def files(self):
        return [self._file_info(file_json) for file_json in
                self._dataset_json.get('documents', [])]

    @property
    def modified_date(self):
        date_string = self.query_dataset_json('info.modifiedDate')
        return dateutil.parser.parse(date_string)

    @property
    def uuid(self):
        return self._dataset_json.get('uuid')

    def download_files(self):
        for url, file_name in self.files:
            self.local_files.append(
                self._download_manager.download_file(url, file_name)
            )
        self.local_file_checksums = checksum_generator.file_checksums(self)
