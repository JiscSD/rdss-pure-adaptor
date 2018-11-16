import logging
from .validator import RDSSMessageValidator
from .message_header import RDSSMessageHeader

logger = logging.getLogger(__name__)

message_validator = RDSSMessageValidator()


class BaseRDSSMessageCreator:
    message_class = ''
    message_type = ''

    def __init__(self, instance_id):
        self._header = RDSSMessageHeader(instance_id)

    def generate(self, message_body):
        message_header = self._header.generate(
            self.message_class,
            self.message_type,
        )
        logger.info('Generating message %s', message_header['messageId'])
        return RDSSMessage(message_header, message_body)


class MetadataCreate(BaseRDSSMessageCreator):
    message_class = 'Event'
    message_type = 'MetadataCreate'


class MetadataUpdate(BaseRDSSMessageCreator):
    message_class = 'Event'
    message_type = 'MetadataUpdate'


class RDSSMessage:

    def __init__(self, message_header, message_body):
        self._message = {
            'messageHeader': message_header,
            'messageBody': message_body
        }
        self.validation_errors = []
        self.validate_body()

    def _set_error(self, error_code, error_description):
        logger.info('Setting the following error on message: %s - %s',
                    error_code, error_description)
        self._message['messageHeader']['errorCode'] = error_code
        self._message['messageHeader']['errorDescription'] = error_description

    def validate_body(self):
        body_errors = message_validator.message_body_errors(
            self._message['messageBody']
        )
        if body_errors:
            self.validation_errors.extend(body_errors)
            self._set_error(*self.error_info)

    @property
    def error_info(self):
        if self.is_valid:
            return '', ''
        else:
            return 'GENERR001', ' | '.join(self.validation_errors)

    @property
    def is_valid(self):
        return not self.validation_errors

    @property
    def as_json(self):
        return self._message
