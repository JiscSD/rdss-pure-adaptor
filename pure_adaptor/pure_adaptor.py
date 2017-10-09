#!/usr/bin/env python
import logging
import os
import sys

from .processor import PureAdaptor

logger = logging.getLogger(__name__)


def all_env_vars_exist(var_names):
    env_vars = {name: os.environ.get(name) for name in var_names}
    if not all(env_vars.values()):
        missing = (name for name, exists in env_vars.items() if not exists)
        err_msg = 'The following env variables have not been set: {}'
        sys.stderr.write(err_msg.format(', '.join(missing)))
        sys.exit(2)


def main():

    required_env_variables = (
        'API_URL',
        'API_VERSION',
        'API_KEY',
        'UPLOAD_BUCKET',
    )
    all_env_vars_exist(required_env_variables)


if __name__ == '__main__':
    main()
