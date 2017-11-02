import abc


class BasePureAPI(abc.ABC):
    """ An Abstract Base Class for interactions with PURE APIs """

    @abc.abstractmethod
    def changed_datasets(self, since_datetime=None):
        pass

    @abc.abstractmethod
    def list_all_datasets(self):
        pass

    @abc.abstractmethod
    def get_dataset(self, uuid):
        pass

    @abc.abstractmethod
    def download_file(self, url, dest):
        pass
