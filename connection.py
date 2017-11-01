#!/usr/bin/env python3
import requests


def main():
    url = 'http://35.177.66.67/'
    try:
        response = requests.head(url)
        print(response.status_code)
        print('{} response: {}'.format(url, response.status_code))
    except requests.exceptions.RequestException as e:
        print('Unable to access{}'.format(url))
        raise


if __name__ == '__main__':
    main()
