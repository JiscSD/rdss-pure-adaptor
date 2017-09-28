import abc

class BasePureAPI(abc.ABC):

    """ An Abstract Base Class for interactions with PURE APIs """
    
    @abc.abstractmethod
    def changed_datasets():
        pass

    @abc.abstractmethod
    def list_all_datasets():
        pass

    @abc.abstractmethod
    def get_dataset():
        pass

    @abc.abstractmethod
    def download_file(self, url, dest):
        pass

