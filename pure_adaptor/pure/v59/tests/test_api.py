import pytest
import urllib

from collections import namedtuple

from api import PureAPI

PureAPIDatasetResponse = namedtuple(
    'PureAPIDatasetResponse', ['json'])

PureHeadResponse = namedtuple(
    'PureHeadResponse', ['raise_for_status'])


def format_dataset_json(items, next_link=None):
    response = {
        'count': 22,
        'items': items
    }
    if next_link:
        response['navigationLink'] = [{'ref': 'next', 'href': next_link}]
    return lambda: response


@pytest.fixture
def endpoint_url():
    return 'https://pure_endpoint_url.ac.uk/ws/api/59/'


@pytest.fixture
def api_key():
    return 'a_uuid_api_key'


def mock_pure_head(url, *args, **kwargs):
    return PureHeadResponse(lambda: True)


def mock_pure_get(url, *args, **kwargs):
    parsed_url = urllib.parse.urlsplit(url)
    qs = urllib.parse.parse_qs(parsed_url[3])
    if qs.get('offset'):
        items = []
        return PureAPIDatasetResponse(format_dataset_json(items))
    else:
        items = []
        qs['offset'] = 20
        parsed_url[3] = urllib.urlencode(qs)
        next_url = urllib.parse.urlunsplit(parsed_url)
        return PureAPIDatasetResponse(format_dataset_json(items, next_url))


class TestPureAPI:

    def setup(self, monkeypatch, endpoint_url, api_key):
        monkeypatch.setattr('requests.get', mock_pure_get)
        monkeypatch.setattr('requests.head', mock_pure_head)

        self.api = PureAPI(endpoint_url, api_key)

    def test_changed_datasets(self):
        self.apig

    def teardown(self):
        pass
