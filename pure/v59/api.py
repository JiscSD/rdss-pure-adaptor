import requests
import collections
import certifi
import urllib
from pure.models import PureDataset

class PureAPI(object):

    """Abstraction over the Pure API v5.9"""

    def __init__(self, endpoint_url, api_key):
        """
        :endpoint_url: The base url of the API endpoint
        :api_key: The api key provided for authentication

        """
        self._split_endpoint_url = urllib.parse.urlsplit(endpoint_url)
        self._api_key = api_key

    def _create_path(self, path):
        path_parts = self._split_endpoint_url[2].split('/')
        path_parts.extend(path.split('/'))
        return "/".join([p for p in path_parts if p])

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

    def _response_items(self, json_dict, items=list(), continue_func=None):
        """ Extracts items from a response and appends them to an existing set
            of responses if provided. If a continue function is provided this
            will be used to filter items and conditionally set a continue flag
            (otherwise True).

            :returns: tuple(bool, list)
            """
        new_items = json_dict.get('items', list())
        cont = True
        if continue_func:
            filtered_new_items = filter(continue_func, new_items)
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
        response = self._get(url, *args, **kwargs)
        return response.json() 

    def _streaming_download(self, url, dest, *args, **kwargs):
        """ Wrapper around the get method to use for streaming download
            of files. .

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

    def list_all_datasets(self, size=20, order='-modified', continue_func=None):
        """ List the metadata objects for all datasets.
            Defaults to most recently modified objects first. 
        :returns: TODO

        """
        endpoint = "/datasets"
        query = {'size': size, 'order': order}
        url = self._create_url(endpoint, query=query)
        json_response = self._get_json(self._create_url(endpoint))
        cont, items = self._response_items(json_response, list(), continue_func)
        next_url = self._navigation_links(json_response).get('next')

        while next_url and cont:
            json_response = self._get_json(next_url)
            cont, items = self._response_items(json_response, items, continue_func)
            next_url = self._navigation_links(json_response).get('next')

        return items

    def get_dataset(self, uuid):
        """ Get the metadata object for a single dataset.

        :uuid: String: ID of the dataset
        :returns: TODO

        """
        endpoint = "/datasets/{uuid}".format(uuid=uuid)
        return self._get_json(self._create_url(endpoint))

    def get_dataset_files(self, url_dest_pairs):
        """  

        """
        downloaded_files = []
        for dest, url in url_dest_pairs:
            self._streaming_download(url, dest)
            downloaded_files.append(dest)
        return downloaded_files
        
