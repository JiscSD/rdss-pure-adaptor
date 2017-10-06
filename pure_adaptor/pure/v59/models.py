import os
import dateutil.parser
import urllib
import jmespath
from pure.base import BasePureDataset
from pure.base import JSONRemapper

from .download_manager import PureDownloadManager

with open(os.path.join(os.path.dirname(__file__),
                       'research_object_mapping.txt'), 'r') as config_in:
    mapper_config = config_in.read()

pure_to_canonical_mapper = JSONRemapper(mapper_config)


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


class PureDataset(BasePureDataset):

    """Abstraction around the dataset responses from the Pure API.
        """

    def __init__(self, dataset_json, pure_api_instance):
        """ Initialises the dataset with the dataset json object returned
            from the Pure API
            """
        if pure_api_instance:
            self._download_manager = PureDownloadManager(pure_api_instance)
        self._dataset_json = dataset_json
        self.local_files = []

    def query_dataset_json(self, query):
        return jmespath.search(query, self._dataset_json)

    def _file_info(self, file_json):
        """ Extracts the url and file name for a file.
            """
        file_name = file_json.get('title')
        url = ws_url_remap(file_json.get('url'))
        return url, file_name

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
        return pure_to_canonical_mapper.remap(self._dataset_json)

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
