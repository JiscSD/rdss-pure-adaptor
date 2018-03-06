import jmespath
from jmespath import functions
import logging
import re

from rdsslib.taxonomy.taxonomy_client import TaxonomyGitClient, DATE_TYPE,\
    RESOURCE_TYPE, PERSON_ROLE, ORGANISATION_TYPE, \
    ValueNotFound, ORGANISATION_ROLE

logger = logging.getLogger(__name__)

TAXONOMY_SCHEMA_REPO = 'https://github.com/JiscRDSS/taxonomyschema.git'
GIT_TAG = 'v0.1.0'


JISC_ID = {
    'University of St Andrews': 799,
}


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
    taxonomy_client = TaxonomyGitClient(TAXONOMY_SCHEMA_REPO, GIT_TAG)

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

    @functions.signature({'types': ['string']})
    def _func_person_role(self, person_role):
        if person_role == 'Creator':
            rdss_name = 'data' + person_role
        else:
            rdss_name = person_role
        mapping = self.taxonomy_client.get_by_name(
            PERSON_ROLE, rdss_name
        )
        return mapping

    @functions.signature({'types': ['string']})
    def _func_jisc_id(self, publisher_name):
        return JISC_ID.get(publisher_name) or 0

    @functions.signature({'types': ['string']})
    def _func_org_type(self, org_type):
        rdss_name = org_type.lower()
        try:
            org_type = self.taxonomy_client.get_by_name(
                ORGANISATION_TYPE, rdss_name
            )
            return org_type
        except ValueNotFound:
            org_type = self.taxonomy_client.get_by_name(
                ORGANISATION_TYPE, 'other'
            )
            return org_type

    @functions.signature({'types': ['string']})
    def _func_org_role(self, org_role):
        rdss_name = org_role.lower()
        return self.taxonomy_client.get_by_name(
            ORGANISATION_ROLE, rdss_name
        )
