from pure import PureAPI, PureDataset
import urllib
from canonical_data_model import PureToRDSSCanonicalDataModel


url = 'https://riswebtest.st-andrews.ac.uk/ws/api/59/'
api_key = 'f39e70b7-c2b2-48a2-8175-92ccc6978128'

test_object_id = '83957a84-2186-4c14-8e55-f961a19ec9a9'

pure_api = PureAPI(url, api_key)

dataset_json = pure_api.get_dataset(test_object_id)

dataset = PureDataset(dataset_json)

def ws_url_remap(pure_data_url):
    """ Modifies a data location url to be http and /portal rather than /ws """
    url_parts = list(urllib.parse.urlsplit(pure_data_url))
    path_parts = [p for p in url_parts[2].split('/') if p]
    url_parts[2] = "/".join(['portal'] + path_parts[1:])
    url_parts[0] = 'http'
    return urllib.parse.urlunsplit(url_parts)

doc_down_paths = [(fs_path, ws_url_remap(url)) 
    for fs_path, url in dataset.document_download_paths()]

# Download dataset
dataset_files = pure_api.get_dataset_files(doc_down_paths)

# Create path structure from DOI


# Upload data, metadata and original_metadata


