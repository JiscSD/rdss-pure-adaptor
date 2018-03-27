import abc


class BasePureDownloadManager(abc.ABC):

    @abc.abstractmethod
    def download_file(self, url, file_name, temp_dir):
        pass
