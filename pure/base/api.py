import abc

class BasePureAPI(abc.ABC):

    """ An Abstract Base Class for interactions with PURE APIs """

    def list_changed_datasets():
        pass

    def list_all_datasets():
        pass

    def get_dataset():
        pass

    def get_dataset_file():
        pass

