import tempfile
import os

from pure.base import BasePureDownloadManager


class PureDownloadManager(BasePureDownloadManager):

    def __init__(self, pure_api):
        self._pure_api = pure_api
        self._temp_dir = None

    @property
    def temp_dir(self):
        """ Initialises a temporary directory to store data files from this
            dataset.
            """
        if not self._temp_dir:
            self._temp_dir = tempfile.TemporaryDirectory()
        return self._temp_dir.name

    def _document_temp_path(self, file_name):
        """ Constructs a path within the temp_dir for a given file.
            """
        return os.path.join(self.temp_dir, file_name)

    def download_file(self, url, file_name):
        dest = self._document_temp_path(file_name)
        self._pure_api.download_file(url, dest)
        return dest
