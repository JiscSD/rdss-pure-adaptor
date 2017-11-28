import hashlib
import os
import logging

logger = logging.getLogger(__name__)


class ChecksumGenerator(object):

    def __init__(self):
        self.hasher = hashlib.sha256

    def _hash_file(self, file_path, buf_size=4096):
        """ Generates the hash of an individual file.
            :file_path: String
            :returns: String
            """
        file_hasher = self.hasher()
        logger.debug('Generating checksum for %s', file_path)
        with open(file_path, 'rb') as f_in:
            for file_chunk in iter(lambda: f_in.read(buf_size), b''):
                file_hasher.update(file_chunk)
        return file_hasher.hexdigest()

    def file_checksums(self, dataset):
        """ Generates checksums for every local file in a dataset,
            returning these checksums as values in a dictionary, with the
            filename as the key.
            :dataset: PureDataset
            :returns: dict
            """
        checksum_dict = {}
        if not dataset.files:
            logger.debug('%s has no associated files to generate checksums'
                         ' for.', dataset)
            return checksum_dict

        if not dataset.local_files:
            logger.error('%s files have not been downloaded prior to checksum'
                         ' generation.', dataset)
            return checksum_dict

        for f_path in dataset.local_files:
            logger.info('Generating %s checksum for %s',
                        self.hasher().name, f_path)
            path_hash = self._hash_file(f_path)
            file_name = os.path.basename(f_path)
            checksum_dict[file_name] = path_hash
        return checksum_dict
