import jmespath 

class JSONRemapper(object):

    """ To effect the remapping of data in one JSON format to another using a 
        config file storing JMESPath expressions."""

    def __init__(self, config_object):
        self._mappings = self._initialise_mappings(config_object)

    def _initialise_mappings(self, config_object):
        #mappings = {key: jmespath.compile(expression) 
        #        for key, expression in config_object.items()}

        return jmespath.compile(config_object)

    def _strip_none_values(self, json_object):
        """ 

        """
        
    def remap(self, json_object):
        #remapped_json = {}
        #for key, expression in self._mappings.items():
        #    result = expression.search(json_object)
        #    if result:
        #        remapped_json[key] = result

        return self._mappings.search(json_object)
