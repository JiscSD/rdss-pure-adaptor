import jmespath
from jmespath import functions
import logging
import re

from rdsslib.taxonomy.taxonomy_client import TaxonomyGitClient, DATE_TYPE,\
    RESOURCE_TYPE

logger = logging.getLogger(__name__)

TAXONOMY_SCHEMA_REPO = 'https://github.com/JiscRDSS/taxonomyschema.git'


class JSONRemapper(object):

    """ To effect the remapping of data in one JSON format to another using a
        config file storing JMESPath expressions."""

    def __init__(self, config_file_path):
        with open(config_file_path, 'r') as config_in:
            mapper_config = config_in.read()
        self._mappings = self._initialise_mappings(mapper_config)

    def _initialise_mappings(self, config_object):
        return jmespath.compile(config_object)

    def remap(self, json_object, custom_funcs=None):
        options = jmespath.Options(custom_functions=custom_funcs)
        return self._mappings.search(json_object, options=options)


class JMESCustomFunctions(functions.Functions):
    """
    Custom JMESPath mapping functions
    """
    taxonomy_client = TaxonomyGitClient(TAXONOMY_SCHEMA_REPO)

    @functions.signature({'types': ['object']})
    def _func_object_date(self, date_dict):
        new_dates = []
        date_regex = re.compile('.*Date')
        for key, value in date_dict.items():
            if date_regex.match(key):
                rdss_name = key.strip('Date')
                mapping = self.taxonomy_client.get_by_name(
                    DATE_TYPE, rdss_name)
                rdss_dateobj = {'dateType': mapping,
                                'dateValue': value}
                new_dates.append(rdss_dateobj)
        return new_dates

    @functions.signature({'types': ['string']})
    def _func_object_resourcetype(self, object_resource):
        rdss_name = object_resource.lower()
        mapping = self.taxonomy_client.get_by_name(
            RESOURCE_TYPE, rdss_name
        )
        return mapping
