import pytest
import os

from collections import namedtuple
from ..checksum import ChecksumGenerator

MockDataset = namedtuple('MockDataset', ['files', 'local_files'])


@pytest.fixture
def test_dataset():
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    files = ['test_dataset_file_one.txt', 'test_dataset_file_two.txt']
    return MockDataset(files, [os.path.join(fixtures_dir, f) for f in files])


@pytest.fixture
def test_checksum_dict():
    """ md5 checksums generated with op"""
    return {
        'test_dataset_file_one.txt':
            'Wtdb7pD6oksoGWCMMkxznQ==',
            'test_dataset_file_two.txt':
            'vVNZXea9pQ2HFk8SzIiz9w=='
    }


def test_file_checksums(test_dataset, test_checksum_dict):
    checksum_generator = ChecksumGenerator()
    checksum_dict = checksum_generator.file_checksums(test_dataset)
    assert test_checksum_dict == checksum_dict
