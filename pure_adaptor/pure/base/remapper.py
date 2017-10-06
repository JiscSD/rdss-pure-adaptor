import jmespath


class JSONRemapper(object):

    """ To effect the remapping of data in one JSON format to another using a
        config file storing JMESPath expressions."""

    def __init__(self, config_object):
        self._mappings = self._initialise_mappings(config_object)

    def _initialise_mappings(self, config_object):
        return jmespath.compile(config_object)

    def _strip_none_values(self, json_object):
        """

        """

    def remap(self, json_object):
        return self._mappings.search(json_object)
