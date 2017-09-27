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
        self._temp_dir = None
    

    def _document_temp_path(self, file_name):
        """ Constructs a path within the temp_dir for a given file. 
            """
        return os.path.join(self.temp_dir, file_name)

    def _document_location(self, document_json):
        """ Extracts the url and file name from a document 
            """
        title = document_json.get('title')
        url = document_json.get('url')
        return title, url
    
    @property
    def metadata(self):
        """ """
        return self._dataset_json
        
    @property
    def doi(self):
        return self._dataset_json.get('doi', "").strip() 

    def documents(self):
        return [self._document_location(doc_obj) for doc_obj in 
                self._dataset_json.get('documents')]
            
    def document_download_paths(self):
        return [(self._document_temp_path(name), url) 
                for name, url in self.documents()]
