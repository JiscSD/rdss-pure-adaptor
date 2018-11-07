import abc
import os
import dateutil.parser
import urllib
import uuid
import jmespath
import logging

from .download_manager import BasePureDownloadManager
from .checksum import ChecksumGenerator
from .remapper import JSONRemapper

logger = logging.getLogger(__name__)


class AbstractPureDataset(abc.ABC):

    @abc.abstractproperty
    def doi_upload_key(self):
        """ The DOI for this dataset if available, or another key in the
            format "no_doi/<header_identifier>"
        :returns: string

        """
        pass

    @abc.abstractproperty
    def original_metadata(self):
        """ The original metadata that this class is instantiated from
            for upload as original_pure_metadata.json.
        :returns: string

        """
        pass

    @abc.abstractproperty
    def rdss_canonical_metadata(self):
        """ The metadata for this dataset mapped to the schema from the
            canonical data model.
        :returns: string
        """
        pass

    @abc.abstractproperty
    def files(self):
        """ A list of urls and file names for all files in this dataset.
        :returns: [(string,string),]
        """
        pass

    @abc.abstractproperty
    def modified_date(self):
        """ The last updated date for the dataset as a python datetime object.
        : returns: datetime.datetime
        """
        pass


class BasePureDataset(AbstractPureDataset):
    """Abstraction around the dataset responses from the Pure API.
        """
    CHECKSUM_GENERATOR = ChecksumGenerator()
    MAPPING_FILE_PATH = os.path.join(
        os.path.dirname(__file__), 'base_mapping.txt')
    DOWNLOAD_MANAGER_CLASS = BasePureDownloadManager

    def __init__(self, dataset_json, pure_api_instance=None):
        """ Initialises the dataset with the dataset json object returned
            from the Pure API
            """
        if pure_api_instance:
            self._download_manager = self.DOWNLOAD_MANAGER_CLASS(
                pure_api_instance)
        self.pure_to_canonical_mapper = JSONRemapper(self.MAPPING_FILE_PATH)
        self._dataset_json = dataset_json
        self.local_files = []
        self.local_file_checksums = {}
        self.local_file_sizes = {}
        self.file_s3_urls = {}

    def __str__(self):
        return 'PureDataset: {}'.format(self.pure_uuid)

    def query_dataset_json(self, query):
        return jmespath.search(query, self._dataset_json)

    def _file_info(self, file_json):
        """ Extracts the url and file name for a file.
            """
        return file_json.get('url'), file_json.get('title')

    def _format_checksum(self, file_name):
        return [{
            'checksumType': 1,  # md5
            'checksumValue': self.local_file_checksums.get(file_name),
            'checksumUuid': str(uuid.uuid4())
        }]

    def _file_name_from_url(self, url):
        return os.path.basename(urllib.parse.urlsplit(url)[2])

    def _format_local_data(self, obj_file):
        file_name = self._file_name_from_url(obj_file['fileIdentifier'])
        obj_file['fileChecksum'] = self._format_checksum(file_name)
        obj_file['fileStorageLocation'] = self.file_s3_urls.get(file_name)
        obj_file['fileStorageStatus'] = 1  # online
        obj_file['fileUploadStatus'] = 2  # uploadComplete
        obj_file['fileSize'] = self.local_file_sizes.get(file_name)
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

    def _calculate_file_sizes(self):
        filesize_dict = {}
        logger.info('Calculating filesizes')
        for f_path in self.local_files:
            f_name = os.path.basename(f_path)
            filesize_dict[f_name] = os.stat(f_path).st_size
        return filesize_dict

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
    def custom_funcs(self):
        return self._custom_funcs

    @custom_funcs.setter
    def custom_funcs(self, value):
        self._custom_funcs = value

    @property
    def rdss_canonical_metadata(self):
        logger.info('Remapping pure dataset %s to canonical metadata.',
                    self.pure_uuid)
        m_data = self.pure_to_canonical_mapper.remap(self._dataset_json,
                                                     custom_funcs=self.custom_funcs)
        final = self._update_with_local_data(m_data)
        return final

    @property
    def files(self):
        return [self._file_info(file_json) for file_json in
                self._dataset_json.get('documents', [])]

    @property
    def modified_date(self):
        date_string = self.query_dataset_json('info.modifiedDate')
        return dateutil.parser.parse(date_string)

    @property
    def pure_uuid(self):
        return self._dataset_json.get('uuid')

    def download_files(self, temp_dir):
        for url, file_name in self.files:
            self.local_files.append(
                self._download_manager.download_file(url, file_name, temp_dir)
            )
        self.local_file_checksums = self.CHECKSUM_GENERATOR.file_checksums(
            self)
        self.local_file_sizes = self._calculate_file_sizes()

    def versioned_rdss_canonical_metadata(self, previous_version_uuid):
        """ Takes an objectUuid of a previous version of this dataset and
            returns an appropriately versioned RDSS CDM of the dataset.
            """
        metadata = self.rdss_canonical_metadata
        related_ids = metadata.get('objectRelatedIdentifier', [])
        related_ids.append({
            'identifier': {
                'identifierValue': previous_version_uuid,
                'identifierType': 16
            },
            'relationType': 9
        })
        metadata['objectRelatedIdentifier'] = related_ids
        return metadata
