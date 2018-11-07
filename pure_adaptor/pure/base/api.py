import abc
import requests
import urllib
import dateutil.parser
import logging

from .models import BasePureDataset
from .download_manager import BasePureDownloadManager

logger = logging.getLogger(__name__)


class AbstractBasePureAPI(abc.ABC):
    """ An Abstract Base Class for interactions with PURE APIs """

    @abc.abstractmethod
    def changed_datasets(self, since_datetime=None):
        pass

    @abc.abstractmethod
    def list_all_datasets(self):
        pass

    @abc.abstractmethod
    def download_file(self, url, dest):
        pass


class BasePureAPI(AbstractBasePureAPI):
    """Base implementation for interactions with the Pure Rest API with JSON responses."""

    API_VERSION = 'Base'
    DATASETS_ENDPOINT_PATH = '/datasets'
    DATASET_CLASS = BasePureDataset
    DOWNLOAD_MANAGER_CLASS = BasePureDownloadManager

    def __init__(self, endpoint_url, api_key):
        """
        :endpoint_url: The base url of the API endpoint
        :api_key: The api key provided for authentication

        """
        self._endpoint_url = endpoint_url
        self._split_endpoint_url = urllib.parse.urlsplit(endpoint_url)
        self._api_key = api_key
        try:
            self._api_is_accessible()
        except requests.exceptions.RequestException:
            logging.exception(
                'PureAPI %s initialisation failed.', self.API_VERSION)

    def __str__(self):
        return 'Pure REST API {}: {}'.format(self.API_VERSION, self._endpoint_url)

    def _api_is_accessible(self, **kwargs):
        """ Checks that the API is accessible and it is possible to
            authenticate against it.
            :returns: Boolean
            """
        url = self._create_url(self.DATASETS_ENDPOINT_PATH)
        kwargs = self._update_headers(kwargs, {'api-key': self._api_key})
        try:
            response = requests.head(url, **kwargs)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.exception('Unable to access Pure API v59 due to: %s', e)

    def _to_dataset(self, dataset_json):
        """ Initialise a PureDataset from dataset json, binding this instance
            of the PureAPI to it for use by the PureDownloadManager.
            """
        return self.DATASET_CLASS(dataset_json, self)

    def _create_path(self, path):
        path_parts = self._split_endpoint_url[2].split('/')
        path_parts.extend(path.split('/'))
        return '/'.join([p for p in path_parts if p])

    def _create_url(self, path, query={}):
        url_parts = [
            self._split_endpoint_url[0],
            self._split_endpoint_url[1],
            self._create_path(path),
            urllib.parse.urlencode(query),
            ''
        ]
        return urllib.parse.urlunsplit(url_parts)

    def _update_headers(self, kwargs_dict, new_headers):
        """ Update the headers in kwargs with new values.

        :kwargs_dict: dict
        :new_headers: dict
        :returns: dict

        """
        headers = kwargs_dict.get('headers', dict())
        kwargs_dict['headers'] = {**headers, **new_headers}
        return kwargs_dict

    def _navigation_links(self, json_dict):
        """ Extracts and returns navigation links from a json response.

        :json_dict: dict
        :returns: dict

        """
        navigation_links = dict()
        for nav_link in json_dict.get('navigationLink', list()):
            navigation_links[nav_link['ref']] = nav_link['href']
        return navigation_links

    def _response_items(self, json_dict, items=list(), cont_func=None):
        """ Extracts items from a response and appends them to an existing set
            of responses if provided. If a continue function is provided this
            will be used to filter items and conditionally set a continue flag
            (otherwise True).

            :returns: tuple(bool, list)
            """
        new_items = json_dict.get('items', list())
        cont = True
        if cont_func:
            filtered_new_items = list(filter(cont_func, new_items))
            if len(filtered_new_items) != len(new_items):
                new_items = filtered_new_items
                cont = False
        return cont, items + new_items

    def _get(self, url, *args, **kwargs):
        """ Abstraction over requests.get that includes PURE api key.
            """
        kwargs = self._update_headers(kwargs, {'api-key': self._api_key})
        return requests.get(url, *args, **kwargs)

    def _get_json(self, url, *args, **kwargs):
        """ GET json from url and return json object
            """
        kwargs = self._update_headers(kwargs, {'Accept': 'application/json'})
        logger.info('Getting json response from %s.', url)
        response = self._get(url, *args, **kwargs)
        return response.json()

    def download_file(self, url, dest, *args, **kwargs):
        """ Wrapper around the get method to use for streaming download
            of files.
            """
        with self._get(url, stream=True) as r:
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
        return dest

    def list_all_datasets(self, size=20, order='-modified', cont_func=None):
        """ List the metadata objects for all datasets.
            Defaults to most recently modified objects first.
        :returns: [PureDataset]

        """
        query = {'size': size, 'order': order}
        url = self._create_url(self.DATASETS_ENDPOINT_PATH)
        json_response = self._get_json(url, params=query)
        cont, items = self._response_items(
            json_response, list(), cont_func)
        next_url = self._navigation_links(json_response).get('next')

        while next_url and cont:
            json_response = self._get_json(next_url)
            cont, items = self._response_items(
                json_response, items, cont_func)
            next_url = self._navigation_links(json_response).get('next')

        return [self._to_dataset(dataset_json) for dataset_json in items]

    def changed_datasets(self, since_datetime=None):
        """ List the metadata objects for all validated datasets that have been modified
            since the provided datetime. If no datetime object is provided then
            will default to listing all the datasets.
        :since_datetime: DateTime
        :returns: [PureDataset]
        """
        def changed_since(dataset_json):
            updated = dataset_json.get('info').get('modifiedDate')
            return dateutil.parser.parse(updated) > since_datetime

        if since_datetime:
            logger.info('Getting all datasets updated since %s from %s.',
                        since_datetime, self._endpoint_url)
            datasets = self.list_all_datasets(cont_func=changed_since)
        else:
            logger.info('Getting all datasets from %s.', self._endpoint_url)
            datasets = self.list_all_datasets()

        def validated(dataset):

            dataset_json = dataset.original_metadata
            workflows = dataset_json['workflow']
            validated = [
                workflow for workflow in workflows if workflow['workflowStep'] == 'validated']
            return len(validated) == len(workflows) and len(workflows) > 0

        return list(filter(validated, datasets))
