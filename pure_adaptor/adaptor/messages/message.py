import json
from .message_header import RDSSMessageHeader


class BaseRDSSMessageCreator:

    def __init__(self, instance_id):
        self._header = RDSSMessageHeader(instance_id)

    def generate(self, payload):
        message_header = self._header.generate(
            self.message_class,
            self.message_type,
        )

        message = {
            'messageHeader': message_header,
            'messageBody': payload
        }

        return RDSSMessage(message)


class MetadataCreate(BaseRDSSMessageCreator):
    message_class = 'Event'
    message_type = 'MetadataCreate'


class MetadataUpdate(BaseRDSSMessageCreator):
    message_class = 'Event'
    message_type = 'MetadataUpdate'


class RDSSMessage:

    def __init__(self, message_json):
        self._message_json = message_json

    def is_valid(self):
        pass

    def output(self):
        return json.dumps(self._message_json)
