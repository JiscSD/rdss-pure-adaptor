#!/usr/bin/env python3

import logging
import os
import sys
import tempfile

from processor import PureAdaptor

logger = logging.getLogger(__name__)
log_formatter = logging.Formatter('%(asctime)s %(name)s:'
                                  ' [%(levelname)s] %(message)s')

std_out_handler = logging.StreamHandler(sys.stdout)
std_out_handler.setFormatter(log_formatter)
std_out_handler.setLevel(logging.DEBUG)
logger.addHandler(std_out_handler)


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
        'RDSS_INTERNAL_INPUT_STREAM',
        'RDSS_MESSAGE_INVALID_STREAM',
        'RDSS_MESSAGE_ERROR_STREAM',
        'JISC_ID'
    )
    env_vars = all_env_vars_exist(required_env_variables)

    try:
        adaptor = PureAdaptor(
            api_version=env_vars['PURE_API_VERSION'],
            api_url=env_vars['PURE_API_URL'],
            api_key=env_vars['PURE_API_KEY'],
            instance_id=env_vars['INSTANCE_ID'],
            input_stream=env_vars['RDSS_INTERNAL_INPUT_STREAM'],
            invalid_stream=env_vars['RDSS_MESSAGE_INVALID_STREAM'],
            error_stream=env_vars['RDSS_MESSAGE_ERROR_STREAM'],
        )
    except Exception:
        logging.exception('Cannot run the Pure Adaptor.')
        sys.exit(1)
    with tempfile.TemporaryDirectory() as temp_dir_path:
        adaptor.run(temp_dir_path)


if __name__ == '__main__':
    main()
