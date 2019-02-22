import logging
from .message_header import RDSSMessageHeader

logger = logging.getLogger(__name__)


class BaseRDSSMessageCreator:
    message_class = ''
    message_type = ''

    def __init__(self, instance_id, schema_validator):
        self._header = RDSSMessageHeader(instance_id)
        self.schema_validator = schema_validator

    def generate(self, message_body):
        message_header = self._header.generate(
            self.message_class,
            self.message_type,
        )
        logger.info('Generating message %s', message_header['messageId'])
        return RDSSMessage(self.schema_validator, message_header, message_body)


class MetadataCreate(BaseRDSSMessageCreator):
    message_class = 'Event'
    message_type = 'MetadataCreate'


class MetadataUpdate(BaseRDSSMessageCreator):
    message_class = 'Event'
    message_type = 'MetadataUpdate'


class RDSSMessage:

    def __init__(self, schema_validator, message_header, message_body):
        self._message = {
            'messageHeader': message_header,
            'messageBody': message_body
        }
        self.schema_validator = schema_validator
        self.validation_errors = []
        self._validate('message_body', self._message['messageBody'])
        self._validate('message', self._message)

    def _validate(self, id_name, json_element):
        _response = self.schema_validator.validate_json_against_schema(
            id_name,
            json_element
        )
        if not bool(_response['valid']):
            self.validation_errors.extend(_response['error_list'])
            self._set_error(*self.error_info)

    def _set_error(self, error_code, error_description):
        logger.info('Setting the following error on message: %s - %s',
                    error_code, error_description)
        self._message['messageHeader']['errorCode'] = error_code
        self._message['messageHeader']['errorDescription'] = error_description

    @property
    def error_info(self):
        if self.is_valid:
            return '', ''
        else:
            return 'GENERR001', ' |\n'.join(
                '{}: {}'.format(e['path'], e['message'])
                for e in self.validation_errors
            )

    @property
    def is_valid(self):
        return not self.validation_errors

    @property
    def as_json(self):
        return self._message
