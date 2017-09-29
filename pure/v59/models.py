import requests
import os
from pure.base import BasePureDataset
from pure.base import JSONRemapper

with open(os.path.join(os.path.dirname(__file__), 'research_object_mapping.txt'), 'r') as config_in:
    mapper_config = config_in.read()

pure_to_canonical_mapper = JSONRemapper(mapper_config)

class PureDataset(BasePureDataset):

    """Abstraction around the dataset responses from the Pure API.
        """

    def __init__(self, dataset_json):
        """ Initialises the dataset with the dataset json object returned
            from the Pure API   
            """
        self._dataset_json = dataset_json

    def _file_info(self, file_json):
        """ Extracts the url and file name for a file. 
            """
        title = file_json.get('title')
        url = file_json.get('url')
        return url, title

    @property
    def doi_upload_key(self):
        return self._dataset_json.get('doi', "") 
    
    @property
    def original_metadata(self):
        """ """
        return self._dataset_json

    @property
    def rdss_canonical_metadata(self):
        return pure_to_canonical_mapper.remap(self._dataset_json) 
        
    @property
    def files(self):
        return [self._file_info(file_json) for file_json in 
                self._dataset_json.get('documents')]
            
