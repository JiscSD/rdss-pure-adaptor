import time
import logging
import boto3
import botocore.exceptions
import json


class KinesisClient(object):
    """Client for managing kinesis messages."""

    def __init__(self, input_stream_name, invalid_stream_name,
                 error_stream_name):
        self.input_stream_name = input_stream_name
        self.invalid_stream_name = invalid_stream_name
        self.error_stream_name = error_stream_name
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.client = boto3.client('kinesis')

    def put_record(self, message):
        """ Take a message and attempt to put in into the input stream.
            Will place the message into the error or invalid streams
            based on the messages class.
            :message: RDSSMessage
            """
        if not message.is_valid:
            self.__move_to_invalid_stream(message.as_json)
        else:
            self.__put_record(self.input_stream_name, message.as_json)

    def __put_record(self, stream_name, payload):
        """Attempt to put the payload in the provided stream name."""
        max_attempts = 6
        attempt = 1

        while attempt <= max_attempts:
            if self.__do_put_record(stream_name, payload, attempt):
                return
            else:
                sleep_seconds = pow(2, attempt) / 10
                self.logger.info(
                    'Backing off for [%s] seconds before attempt [%s]/[%s]',
                    sleep_seconds,
                    attempt,
                    max_attempts
                )
                time.sleep(sleep_seconds)
                attempt += 1

        self.logger.error(
            'Unable to add payload [%s] to Kinesis Stream [%s] - maximum '
            'retries exceeded',
            payload,
            stream_name
        )

        self.move_to_error_stream(
            payload,
            'GENERR005',
            'Maximum retry attempts [%s] exceed for stream [%s]' % (
                max_attempts,
                stream_name
            )
        )

    def __do_put_record(self, stream_name, payload, attempt):
        """Put the payload in the provided stream."""
        self.logger.info(
            'Executing attempt [%s] at adding payload [%s] to stream [%s]',
            attempt,
            payload,
            stream_name
        )

        try:
            self.client.put_record(
                StreamName=stream_name,
                Data=payload,
                PartitionKey=str(int(time.time() * 1000))
            )
            return True
        except botocore.exceptions.ClientError as ce:
            self.logger.exception('Exception: [%s]', ce)
            self.logger.exception(
                'An error occured adding payload [%s] to stream [%s]',
                payload,
                stream_name
            )
            return False

    def move_to_error_stream(self, payload, error_code, error_description):
        try:
            self.logger.info(
                'Setting \'errorCode\' [%s] and \'errorDescription\' [%s] on '
                'payload [%s]',
                error_code,
                error_description,
                payload
            )

            try:
                payload_json = json.loads(payload)
            except ValueError:
                self.__move_to_invalid_stream(payload_json)
                return

            payload_json['messageHeader']['errorCode'] = error_code
            payload_json['messageHeader'][
                'errorDescription'] = error_description
            payload = json.dumps(payload_json)

            self.logger.info(
                'Moving erroneous payload [%s] to stream [%s] with code [%s] '
                'and description [%s]',
                payload,
                self.error_stream_name,
                error_code,
                error_description
            )

            self.__do_put_record(self.error_stream_name, payload, 1)
        except Exception:
            self.logger.exception(
                'Unable to move payload [%s] to stream [%s]',
                payload,
                self.error_stream_name
            )

    def __move_to_invalid_stream(self, payload):
        try:
            self.logger.info(
                'Moving invalid JSON payload [%s] to stream [%s]',
                payload,
                self.invalid_stream_name
            )
            self.__do_put_record(self.invalid_stream_name, payload, 1)
        except Exception:
            self.logger.exception(
                'Unable to move payload [%s] to stream [%s]',
                payload,
                self.invalid_stream_name
            )
