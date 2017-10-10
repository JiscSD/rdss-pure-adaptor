from .message_header import RDSSMessageHeader


class BaseRDSSMessage:

    def __init__(self, environment):
        self._header = RDSSMessageHeader(environment)

    def generate(self, payload):
        message_header = self._header(
            self.message_class,
            self.message_type,
        )

        message = {
            'messageHeader': self._header.generate(),
            'messageBody': payload
        }


class MetadataCreate(BaseRDSSMessage):
    message_class = 'MetadataCreate'
    message_type = 'MetadataCreate'
