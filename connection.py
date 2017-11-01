#!/usr/bin/env python3
import sys
import logging
import requests

logger = logging.getLogger(__name__)
log_formatter = logging.Formatter('%(asctime)s %(name)s:'
                                  ' [%(levelname)s] %(message)s')

std_out_handler = logging.StreamHandler(sys.stdout)
std_out_handler.setFormatter(log_formatter)
std_out_handler.setLevel(logging.INFO)
logger.addHandler(std_out_handler)


def main():
    url = 'https://www.st-andrews.ac.uk/'
    try:
        response = requests.head(url)
        print(response.status_code)
        logging.info('%s response: %s', url, response.status_code)
    except requests.exceptions.RequestException as e:
        logging.error('Unable to access %s', url)
        raise


if __name__ == '__main__':
    main()
