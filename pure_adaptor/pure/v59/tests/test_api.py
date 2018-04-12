import pytest
import urllib
import datetime

from collections import namedtuple

from ..api import PureAPI

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


def mock_dataset(modified_datetime):
    return {
        'info': {
            'modifiedDate': modified_datetime.isoformat()
        }
    }


@pytest.fixture
def a_month_of_dates():
    now = datetime.datetime.now(datetime.timezone.utc)
    return [now - datetime.timedelta(a) for a in range(30)]


@pytest.fixture
def a_month_of_datasets(a_month_of_dates):
    return [mock_dataset(day) for day in a_month_of_dates]


def pure_get(datasets):
    def mock_pure_get(url, *args, **kwargs):
        parsed_url = urllib.parse.urlsplit(url)
        qs = urllib.parse.parse_qs(parsed_url[3])
        if qs.get('offset'):
            items = datasets[20:]
            return PureAPIDatasetResponse(format_dataset_json(items))
        else:
            items = datasets[:20]
            qs['offset'] = 20
            next_url = urllib.parse.urlunsplit((
                *parsed_url[:3],
                urllib.parse.urlencode(qs, doseq=True),
                ''))
            return PureAPIDatasetResponse(format_dataset_json(items, next_url))
    return mock_pure_get


@pytest.fixture(autouse=True)
def pure_head(monkeypatch):

    def mock_pure_head(url, *args, **kwargs):
        return PureHeadResponse(lambda: True)

    monkeypatch.setattr('requests.head', mock_pure_head)


class TestPureAPI:

    def setup(self):
        self.endpoint_url = 'https://pure_endpoint_url.ac.uk/ws/api/59/'
        self.api_key = 'a_uuid_api_key'
        self.api = PureAPI(self.endpoint_url, self.api_key)

    def test_changed_datasets(self, monkeypatch, a_month_of_datasets):
        """ Call the changed_datasets function without a since_datetime to
            list all datasets from the api.
            """
        monkeypatch.setattr('requests.get', pure_get(a_month_of_datasets))

        datasets = self.api.changed_datasets()
        assert len(datasets) == len(a_month_of_datasets)

    def test_changed_datasets_with_since_datetime(self, monkeypatch, a_month_of_datasets,
                                                  a_month_of_dates):
        """ Call the changed_datasets function with a since_datetime to
            list only datasets modified since that datetime. API pagination
            defaults to 20 items.
            """
        monkeypatch.setattr('requests.get', pure_get(a_month_of_datasets))

        ten_days = a_month_of_dates[:10]
        eleventh_day = a_month_of_dates[10]
        twenty_two_days = a_month_of_dates[:22]
        twenty_third_day = a_month_of_dates[22]
        ten_datasets = self.api.changed_datasets(eleventh_day)
        twenty_two_datasets = self.api.changed_datasets(twenty_third_day)
        assert len(ten_days) == len(ten_datasets)
        assert len(twenty_two_days) == len(twenty_two_datasets)

    def teardown(self):
        pass
