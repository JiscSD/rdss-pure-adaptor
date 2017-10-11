import json

from .message_header import RDSSMessageHeader


class BaseRDSSMessage:

    def __init__(self, environment):
        self._header = RDSSMessageHeader(environment)

    def generate(self, payload):
        message_header = self._header.generate(
            self.message_class,
            self.message_type,
        )

        message = {
            'messageHeader': message_header,
            'messageBody': payload
        }

        return json.dumps(message) 


class MetadataCreate(BaseRDSSMessage):
    message_class = 'Event'
    message_type = 'MetadataCreate'


class MetadataUpdate(BaseRDSSMessage):
    message_class = 'Event'
    message_type = 'MetadataUpdate'
