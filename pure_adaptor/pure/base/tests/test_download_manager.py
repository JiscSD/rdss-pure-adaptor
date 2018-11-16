import pytest
import shutil
import tempfile
import os
from collections import namedtuple

from ..download_manager import BasePureDownloadManager


@pytest.fixture
def mock_pure_api():
    MockAPI = namedtuple('MockAPI', ['download_file'])
    return MockAPI(
        lambda url, dest: shutil.copyfile(url, dest)
    )


@pytest.fixture
def temp_dir_path():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_url_name_pairs():
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    files = ['test_dataset_file_one.txt', 'test_dataset_file_two.txt']
    return [(os.path.join(fixtures_dir, f), f) for f in files]


def test_download_manager(mock_pure_api, mock_url_name_pairs, temp_dir_path):
    download_manager = BasePureDownloadManager(mock_pure_api)
    local_files = [download_manager.download_file(*pair, temp_dir_path)
                   for pair in mock_url_name_pairs]
    for f_path in local_files:
        assert os.path.exists(f_path) is True
