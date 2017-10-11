import jmespath

class JSONRemapper(object):

    """ To effect the remapping of data in one JSON format to another using a
        config file storing JMESPath expressions."""

    def __init__(self, config_file_path):
        with open(config_file_path, 'r') as config_in:
            mapper_config = config_in.read()
        self._mappings = self._initialise_mappings(mapper_config)

    def _initialise_mappings(self, config_object):
        return jmespath.compile(config_object)

    def remap(self, json_object):
        return self._mappings.search(json_object)
