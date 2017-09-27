import tempfile


class PureDownloadManager(object):
    
    def __init__(self, pure_api):
        self._pure_api = pure_api

    @property
    def temp_dir(self):
        """ Initialises a temporary directory to store data files from this 
            dataset.
            """
        if not self._temp_dir:
            self._temp_dir = tempfile.TemporaryDirectory()
        return self._temp_dir.name

