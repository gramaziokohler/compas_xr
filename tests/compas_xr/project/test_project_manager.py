import tempfile

import pytest
import json
from compas_xr.project import ProjectManager


@pytest.fixture
def config_path():
    config_path = tempfile.mktemp(suffix=".json", prefix="config_compas_xr")
    with open(config_path, "w+") as config_file:
        data = {
            "apiKey": "x123x123",
            "authDomain": "x123.firebaseapp.com",
            "databaseURL": "https://x123-default-rtdb.europe-west1.firebasedatabase.app",
            "storageBucket": "x123.appspot.com",
        }
        json.dump(data, config_file)
    return config_path


def test_project_manager(config_path):
    pm = ProjectManager(config_path)
    assert pm is not None
