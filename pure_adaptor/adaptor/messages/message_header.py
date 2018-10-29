import re
import uuid
import datetime
import subprocess

RDSS_ERROR_CODES = {
    'GENERR001': 'The Message Body is not in the expected format, for example'
    'mandatory fields are missing.',
    'GENERR002': 'The provided messageType is not supported.',
    'GENERR003': 'The expiration date of the Message had passed at the point'
    'at which delivery was attempted.',
    'GENERR004': 'Invalid, missing or corrupt headers were detected on the'
    'Message.',
    'GENERR005': 'Maximum number of connection retries exceeded when'
    'attempting to send the Message.',
    'GENERR006': 'An error occurred interacting with the underlying system.',
    'GENERR007': 'Malformed JSON was detected in the Message Body.',
    'GENERR008': 'An attempt to roll back a transaction failed.',
    'GENERR009': 'An unexpected or unknown error occurred.',
    'GENERR010': 'Received an invalid / malformed UUID.',
    'APPERRMET001': 'Received a Metadata UPDATE with a datasetUuid that does'
    'not exist.',
    'APPERRMET002': 'Received a Metadata DELETE with a datasetUuid that does'
    'not exist.',
    'APPERRMET003': 'Received a Metadata READ with a datasetUuid that does'
    'not exist.',
    'APPERRVOC002': 'Received a Vocabulary READ with a vocabularyId that does'
    'not exist.',
}


class RDSSMessageHeader(object):

    MESSAGE_CLASSES = (
        'Command',
        'Event',
        'Document'
    )

    MESSAGE_TYPES = (
        'VocabularyRead',
        'VocabularyPatch',
        'MetadataRead',
        'MetadataCreate',
        'MetadataUpdate',
        'MetadataDelete'
    )

    MESSAGE_API_VERSION = '3.0.2'

    UUID_REGEX = re.compile(r'''
            ^[0-9a-f]{8}
            -
            [0-9a-f]{4}
            -
            [1-5][0-9a-f]{3}
            -
            [89ab][0-9a-f]{3}
            -
            [0-9a-f]{12}
            $
            ''', re.VERBOSE | re.IGNORECASE)

    def __init__(self, instance_id):
        self._machine_id = instance_id
        self._machine_address = self._get_machine_ip()

    def _get_machine_ip(self):
        return subprocess.check_output(
            ['sh', '-c', "/sbin/ip route|awk '/default/ { print $3 }'"]
        ).decode('utf-8').strip()

    def _message_id(self):
        return str(uuid.uuid4())

    def _correlation_id(self, correlation_id):
        if not self.UUID_REGEX.match(correlation_id):
            error_str = '{} is not a valid UUID.'.format(correlation_id)
            raise ValueError(error_str)
        return correlation_id

    def _message_class(self, message_class):
        if message_class not in self.MESSAGE_CLASSES:
            error_str = '{} is not among supported message classes:{}'.format(
                message_class, self.MESSAGE_CLASSES)
            raise ValueError(error_str)
        return message_class

    def _message_type(self, message_type):
        if message_type not in self.MESSAGE_TYPES:
            error_str = '{} is not among supported message types:{}'.format(
                message_type, self.MESSAGE_TYPES)
            raise ValueError(error_str)
        return message_type

    def _message_timings(self, now, expiration=None):
        timings = {
            'publishedTimestamp': now.isoformat(),
        }
        if expiration:
            timings['expirationTimestamp'] = expiration
        return timings

    def _message_sequence(self, sequence_identifier, position, total):
        return {
            'sequence': sequence_identifier,
            'position': position,
            'total': total
        }

    def _message_history(self, now):
        return [{
            'machineId': self._machine_id,
            'machineAddress': self._machine_address,
            'timestamp': now.isoformat()
        }]

    def _error_code(self, error_code):
        if error_code not in RDSS_ERROR_CODES.keys():
            error_str = '{} is not a valid RDSS error code.'.format(
                error_code)
            raise ValueError(error_str)
        return error_code

    def generate(self,
                 message_class,
                 message_type,
                 correlation_id=None,
                 return_address=None,
                 message_sequence=None,
                 error_code=None,
                 error_description=None):

        now = datetime.datetime.now(datetime.timezone.utc)

        fields = {
            'messageId': self._message_id(),
            'messageClass': self._message_class(message_class),
            'messageType': self._message_type(message_type),
            'messageTimings': self._message_timings(now),
            'messageHistory': self._message_history(now),
            'version': self.MESSAGE_API_VERSION,
            'generator': 'pure-adaptor'
        }

        if correlation_id:
            fields['correlationId'] = self._correlation_id(correlation_id)

        if return_address:
            fields['returnAddress'] = return_address

        if message_sequence:
            fields['messageSequence'] = self._message_sequence(
                *message_sequence)

        if error_code:
            fields['errorCode'] = self._error_code(error_code)

        if error_description:
            fields['errorDescription'] = error_description

        return fields
