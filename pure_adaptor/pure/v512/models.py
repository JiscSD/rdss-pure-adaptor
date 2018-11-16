import os
import urllib
import logging
from ..base import BasePureDataset

logger = logging.getLogger(__name__)


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

    MAPPING_FILE_PATH = os.path.join(os.path.dirname(
        __file__), 'research_object_mapping.txt')

    def _file_info(self, file_json):
        """ Extracts the url and file name for a file.
            """
        file_name = file_json.get('title')
        url = ws_url_remap(file_json.get('url'))
        return url, file_name
