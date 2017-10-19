import json
import jsonschema
import os


class RDSSMessageValidator:

    base_dir = os.path.dirname(__file__)

    schema_dict = {
        'schemas/enumeration.json':
            'https://www.jisc.ac.uk/rdss/schema/enumeration.json/#',

            'schemas/intellectual_asset.json':
            'https://www.jisc.ac.uk/rdss/schema/intellectual_asset.json/#',

            'schemas/material_asset.json':
            'https://www.jisc.ac.uk/rdss/schema/material_asset.json/#',

            'schemas/research_object.json':
            'https://www.jisc.ac.uk/rdss/schema/research_object.json/#',

            'schemas/types.json':
            'https://www.jisc.ac.uk/rdss/schema/types.json/#'
    }

    body_schema = {
        'id': 'https://www.jisc.ac.uk/rdss/schema/messages/body/metadata/'
        'create/request_schema.json/#',
        '$schema': 'http://json-schema.org/draft-04/schema#',
        '$ref': 'https://www.jisc.ac.uk/rdss/schema/research_object.json/'
        '#/definitions/object'
    }

    def __init__(self):
        self.resolver = jsonschema.RefResolver(
            '',
            {},
            store={
                schema_id: self._open_schema(schema_path)
                for schema_path, schema_id in self.schema_dict.items()
            }
        )
        validator_cls = jsonschema.validators.validator_for(self.body_schema)
        self.body_validator = validator_cls(
            self.body_schema, resolver=self.resolver)

    def _open_schema(self, schema_path):
        with open(os.path.join(self.base_dir, schema_path)) as schema_data:
            return json.load(schema_data)

    def message_body_is_valid(self, message_body):
        return self.body_validator.is_valid(message_body)

    def message_body_errors(self, message_body):
        error_strings = []
        for error in self.body_validator.iter_errors(message_body):
            error_strings.append('{}: {}'.format('.'.join(
                map(str, error.path)), error.message))
        return error_strings
