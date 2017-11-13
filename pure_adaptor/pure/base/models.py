import abc


class BasePureDataset(abc.ABC):

    @abc.abstractproperty
    def doi_upload_key(self):
        """ The DOI for this dataset if available, or another key in the
            format "no_doi/<header_identifier>"
        :returns: string

        """
        pass

    @abc.abstractproperty
    def original_metadata(self):
        """ The original metadata that this class is instantiated from
            for upload as original_pure_metadata.json.
        :returns: string

        """
        pass

    @abc.abstractproperty
    def rdss_canonical_metadata(self):
        """ The metadata for this dataset mapped to the schema from the
            canonical data model.
        :returns: string
        """
        pass

    @abc.abstractproperty
    def files(self):
        """ A list of urls and file names for all files in this dataset.
        :returns: [(string,string),]
        """
        pass

    @abc.abstractproperty
    def modified_date(self):
        """ The last updated date for the dataset as a python datetime object.
        : returns: datetime.datetime
        """
        pass
