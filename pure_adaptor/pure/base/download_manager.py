import abc


class BasePureDownloadManager(abc.ABC):

    @abc.abstractproperty
    def temp_dir(self):
        pass

    @abc.abstractmethod
    def download_file(self, url, file_name):
        pass
