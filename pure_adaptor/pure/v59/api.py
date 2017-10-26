import requests
import urllib
import dateutil.parser
import logging

from ..base import BasePureAPI
from .models import PureDataset

logger = logging.getLogger(__name__)


class PureAPI(BasePureAPI):

    """Abstraction over the Pure API v5.9"""

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
            logging.error('PureAPI v59 initialisation failed.')
            raise

    def __str__(self):
        return 'Pure REST API v5.9: {}'.format(self._endpoint_url)

    def _api_is_accessible(self, **kwargs):
        """ Checks that the API is accessible and it is possible to
            authenticate against it.
            :returns: Boolean
            """
        endpoint = '/datasets'
        url = self._create_url(endpoint)
        kwargs = self._update_headers(kwargs, {'api-key': self._api_key})
        kwargs['verify'] = False
        try:
            response = requests.head(url, **kwargs)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error('Unable to access Pure API v59 due to: %s', e)
            raise

    def _to_dataset(self, dataset_json):
        """ Initialise a PureDataset from dataset json, binding this instance
            of the PureAPI to it for use by the PureDownloadManager.
            """
        return PureDataset(dataset_json, self)

    def _create_path(self, path):
        path_parts = self._split_endpoint_url[2].split('/')
        path_parts.extend(path.split('/'))
        return '/'.join([p for p in path_parts if p])

    def _create_url(self, path, query={}):
        """ TODO: Docstring for _create_url.

        :paths: TODO
        :returns: TODO

        """
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
        """Abstraction over requests.get that includes PURE api key.

        :url: TODO
        :*args: TODO
        :**kwargs: TODO
        :returns: TODO

        """
        kwargs = self._update_headers(kwargs, {'api-key': self._api_key})
        kwargs['verify'] = False
        return requests.get(url, *args, **kwargs)

    def _get_json(self, url, *args, **kwargs):
        """ GET json from url and return json object

        :url: TODO
        :*args: TODO
        :**kwargs: TODO
        :returns: TODO

        """
        kwargs = self._update_headers(kwargs, {'Accept': 'application/json'})
        logger.info('Getting json response from %s.', url)
        response = self._get(url, *args, **kwargs)
        return response.json()

    def download_file(self, url, dest, *args, **kwargs):
        """ Wrapper around the get method to use for streaming download
            of files.

        :url: TODO
        :dest: TODO
        :*args: TODO
        :**kwargs: TODO
        :returns: TODO

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
        endpoint = '/datasets'
        query = {'size': size, 'order': order}
        url = self._create_url(endpoint, query=query)
        json_response = self._get_json(url)
        cont, items = self._response_items(
            json_response, list(), cont_func)
        next_url = self._navigation_links(json_response).get('next')

        while next_url and cont:
            json_response = self._get_json(next_url)
            cont, items = self._response_items(
                json_response, items, cont_func)
            next_url = self._navigation_links(json_response).get('next')

        return [self._to_dataset(dataset_json) for dataset_json in items]

    def get_dataset(self, uuid):
        """ Get the metadata object for a single dataset.

        :uuid: String: ID of the dataset
        :returns: PureDataset

        """
        endpoint = '/datasets/{uuid}'.format(uuid=uuid)
        dataset_json = self._get_json(self._create_url(endpoint))
        return self._to_dataset(dataset_json)

    def changed_datasets(self, since_datetime=None):
        """ List the metadata objects for all datasets that have been modified
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
            return self.list_all_datasets(cont_func=changed_since)
        else:
            logger.info('Getting all datasets from %s.', self._endpoint_url)
            return self.list_all_datasets()
