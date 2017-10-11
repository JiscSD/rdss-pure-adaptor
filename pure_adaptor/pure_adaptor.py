#!/usr/bin/env python
import logging
import os
import sys

from .processor import PureAdaptor

logger = logging.getLogger(__name__)


def all_env_vars_exist(var_names):
    """ Ensure all environment variables exist and return.
        """
    env_vars = {name: os.environ.get(name) for name in var_names}
    if not all(env_vars.values()):
        missing = (name for name, exists in env_vars.items() if not exists)
        err_msg = 'The following env variables have not been set: {}'
        sys.stderr.write(err_msg.format(', '.join(missing)))
        sys.exit(2)
    return env_vars


def main():

    required_env_variables = (
        'API_VERSION',
        'API_URL',
        'API_KEY',
        'UPLOAD_BUCKET',
    )
    env_vars = all_env_vars_exist(required_env_variables)

    adaptor = PureAdaptor(
            api_version = env_vars['API_VERSION']
            api_url = env_vars['API_URL']
            api_key = env_vars['API_KEY']

            )

    adaptor.run()

if __name__ == '__main__':
    main()
