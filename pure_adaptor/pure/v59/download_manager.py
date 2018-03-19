import os
import logging

from ..base import BasePureDownloadManager

logger = logging.getLogger(__name__)


class PureDownloadManager(BasePureDownloadManager):

    def __init__(self, pure_api):
        self._pure_api = pure_api

    def download_file(self, url, file_name, temp_dir):
        dest = os.path.join(temp_dir, file_name)
        logger.info('Downloading %s to %s', url, dest)
        self._pure_api.download_file(url, dest)
        return dest
