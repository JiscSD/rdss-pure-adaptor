import json
import os
import pytest

fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')


def json_from_fixture_file(f_name):
    with open(os.path.join(fixtures_dir, f_name), 'r') as f_in:
        return json.load(f_in.read())


@pytest.fixture
def pure_v59_dataset_multiple_files():
    return json_from_fixture_file('pure_v59_dataset_multiple_files.json')
