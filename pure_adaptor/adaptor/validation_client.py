import logging
import requests
import os
import urllib

logger = logging.getLogger(__name__)


class SchemaValidationClient(object):

    validation_path = 'schema_validation'
    info_path = 'specification_information'

    def __init__(self, validator_base_url, schema_version, schema_ids):
        self.validator_base_url = validator_base_url
        self.schema_version = schema_version
        self.schema_ids = schema_ids
        self._check_api()

    def _create_url(self, *path_elements):
        return urllib.parse.urljoin(
            self.validator_base_url,
            os.path.join(*path_elements, '')
        )

    def _check_api(self):
        """ Provides a check that the API is accessible and the schema_version and schema_ids defined
            for the SchemaValidationClient are valid.
            """
        url = self._create_url(self.info_path, self.schema_version)
        response = requests.get(url)
        response.raise_for_status()
        valid_ids = response.json().get('schema_identifiers')
        for schema_id in self.schema_ids.values():
            if schema_id not in valid_ids:
                raise ValueError('{} not among schema ids for {}'.format(
                    schema_id, self.schema_version))
        logger.info('Confirmed %s is accessible and can validate %s from version %s of the spec',
                    self.validator_base_url,
                    ', '.join(self.schema_ids.values()),
                    self.schema_version)

    def validate_json_against_schema(self, id_name, json_element):
        logger.info('Validating against %s schema', self.schema_ids[id_name])
        response = requests.post(
            self._create_url(self.validation_path, self.schema_version),
            json={
                'schema_id': self.schema_ids[id_name],
                'json_element': json_element
            }
        )
        response.raise_for_status()
        logger.info('Validation service response: %s', response.json())
        return response.json()
