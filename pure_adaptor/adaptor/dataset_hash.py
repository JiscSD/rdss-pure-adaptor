import hashlib
import os


class DatasetHasher(object):

    def __init__(self):
        self.hasher = hashlib.sha256

    def _hash_file(self, file_path, buf_size=4096):
        file_hasher = self.hasher()
        with open(file_path, 'rb') as f_in:
            for file_chunk in iter(lambda: f_in.read(buf_size), b''):
                file_hasher.update(file_chunk)
        return file_hasher.hexdigest()

    def _hash_string(self, string):
        str_hasher = self.hasher()
        str_hasher.update(string.encode())
        return str_hasher.hexdigest()

    def file_checksums(self, dataset):
        checksum_dict = {}
        if not dataset.files:
            return
        if not dataset.local_files:
            print('TODO: files have not been downloaded yet')
            return
        for f_path in dataset.local_files:
            path_hash = self._hash_file(f_path)
            file_name = os.path.basename(f_path)
            checksum_dict[file_name] = path_hash
        return checksum_dict
