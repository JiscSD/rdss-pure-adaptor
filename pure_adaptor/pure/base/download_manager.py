import abc


class BasePureDownloadManager(abc.ABC):

    def __init__(self):
        """TODO: to be defined1. """

    @abc.abstractproperty
    def temp_dir(self):
        pass

    @abc.abstractmethod
    def download_file(self, url, file_name):
        """

        :returns: string
        """
        pass
