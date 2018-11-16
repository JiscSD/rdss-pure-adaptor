import os
import json
import dateutil.parser
import mock
from collections import namedtuple
from urllib.parse import parse_qs

from ..api import PureAPI

PureAPIHeadResponse = namedtuple(
    'PureAPIHeadResponse', ['raise_for_status'])

PureAPIDatasetResponse = namedtuple(
    'PureAPIDatasetResponse', ['json'])


def _load_json(path):
    with open(path, 'r') as f_in:
        return json.load(f_in)


def pure_get_responses(*args, **kwargs):
    def response_path(i): return os.path.join(
        os.path.dirname(__file__),
        'fixtures/pure_512_api_response_{}.json'.format(i)
    )

    offset = parse_qs(args[0]).get('offset', ['0'])[0]
    return PureAPIDatasetResponse(lambda: _load_json(response_path(offset)))


@mock.patch('requests.get')
@mock.patch('requests.head')
def test_changed_datasets(mock_requests_head, mock_requests_get):
    mock_requests_head.return_value = PureAPIHeadResponse(lambda: True)
    mock_requests_get.side_effect = pure_get_responses
    pure_api_endpoint = 'https://an_institution.with_pure.ac.uk/ws/api/512/'
    pure_api = PureAPI(pure_api_endpoint, 'an_auth_uuid')
    datasets = pure_api.changed_datasets()
    # One should be excluded as not having been validated
    assert len(datasets) == 3


@mock.patch('requests.get')
@mock.patch('requests.head')
def test_changed_datasets_with_since_datetime(mock_requests_head, mock_requests_get):
    mock_requests_head.return_value = PureAPIHeadResponse(lambda: True)
    mock_requests_get.side_effect = pure_get_responses
    pure_api_endpoint = 'https://an_institution.with_pure.ac.uk/ws/api/512/'
    pure_api = PureAPI(pure_api_endpoint, 'an_auth_uuid')
    since_datetime = dateutil.parser.parse('2017-04-01T00:00:00.000+0000')
    datasets = pure_api.changed_datasets(since_datetime)
    # One should be excluded as not having been validated
    # One excluded as being from before the since_datetime
    assert len(datasets) == 2
