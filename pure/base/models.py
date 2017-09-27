import abc

class BasePureDataset(abc.ABC):

    """ An Abstract Base Class for interactions with PURE APIs """

    def __init__(self):
        """TODO: to be defined1. """
        abc.ABC.__init__(self)

    def documents(self):
        pass

    def doi(self):
        pass

    def metadata(self):
        pass
