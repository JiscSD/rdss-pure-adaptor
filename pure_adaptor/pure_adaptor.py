#!/usr/bin/env python
import logging
import os
import sys

from processor import PureAdaptor

logger = logging.getLogger(__name__)
std_out_handler = logging.StreamHandler(sys.stdout)
std_out_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
std_out_handler.setLevel(logging.INFO)
logger.addHandler(std_out_handler)
logger.setLevel(logging.INFO)


def all_env_vars_exist(var_names):
    """ Ensure all environment variables exist and return them.
        """
    env_vars = {name: os.environ.get(name) for name in var_names}
    if not all(env_vars.values()):
        missing = (name for name, exists in env_vars.items() if not exists)
        logger.error('The following env variables have not been set: %s',
                     ', '.join(missing))
        sys.exit(2)
    return env_vars


def main():

    required_env_variables = (
        'PURE_API_VERSION',
        'PURE_API_URL',
        'PURE_API_KEY',
        'INSTANCE_ID',
        'RDSS_INTERNAL_INPUT_QUEUE',
        'RDSS_MESSAGE_INVALID_QUEUE',
        'RDSS_MESSAGE_ERROR_QUEUE',
    )
    env_vars = all_env_vars_exist(required_env_variables)

    adaptor = PureAdaptor(
        api_version=env_vars['PURE_API_VERSION'],
        api_url=env_vars['PURE_API_URL'],
        api_key=env_vars['PURE_API_KEY'],
        instance_id=env_vars['INSTANCE_ID'],
        input_queue=env_vars['RDSS_INTERNAL_INPUT_QUEUE'],
        invalid_queue=env_vars['RDSS_MESSAGE_INVALID_QUEUE'],
        error_queue=env_vars['RDSS_MESSAGE_ERROR_QUEUE'],
    )

    adaptor.run()


if __name__ == '__main__':
    main()
