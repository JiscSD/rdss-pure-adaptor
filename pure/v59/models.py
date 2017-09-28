import requests
import os

class PureDataset(object):

    """Abstraction around the dataset responses from the Pure API.
        """

    def __init__(self, dataset_json):
        """ Initialises the dataset with the dataset json object returned
            from the Pure API   
            """
        self._dataset_json = dataset_json

    def _document_info(self, document_json):
        """ Extracts the url and file name for a document 
            """
        title = document_json.get('title')
        url = document_json.get('url')
        return url, title
    
    @property
    def metadata(self):
        """ """
        return self._dataset_json
        
    @property
    def doi(self):
        return self._dataset_json.get('doi', "") 

    def documents(self):
        return [self._document_info(doc_obj) for doc_obj in 
                self._dataset_json.get('documents')]
            
