import abc
import os
import logging

logger = logging.getLogger(__name__)


class AbstractPureDownloadManager(abc.ABC):

    @abc.abstractmethod
    def download_file(self, url, file_name, temp_dir):
        pass


class BasePureDownloadManager(AbstractPureDownloadManager):

    def __init__(self, pure_api):
        self._pure_api = pure_api

    def download_file(self, url, file_name, temp_dir):
        dest = os.path.join(temp_dir, file_name)
        logger.info('Downloading %s to %s', url, dest)
        self._pure_api.download_file(url, dest)
        return dest
