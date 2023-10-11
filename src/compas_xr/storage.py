import pyrebase
import json
import os
from compas_xr import SCRIPT

class Storage(object):

    # Class attribute for the shared firebase storage reference
    _shared_storage = None

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.default_config_path = os.path.abspath(os.path.join(SCRIPT, "firebase_config.json"))
        self._ensure_storage()

    def _ensure_storage(self):
        # Initialize firebase connection and storage only once
        if not Storage._shared_storage:
            path = self.config_path or Storage.default_config_path

            # Load the firebase configuration file from the JSON file if it exists: Else: Print.
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)

            firebase = pyrebase.initialize_app(config)
            Storage._shared_storage = firebase.storage()

        # Still no storage? Fail, we can't do anything
        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

    def upload_to_firebase(self, path_on_cloud, path_local):
        self._ensure_storage()
        Storage._shared_storage.child(path_on_cloud).put(path_local)

    def download_from_firebase(self, path_on_cloud, path_local):
        self._ensure_storage()
        filename = path_local
        Storage._shared_storage.child(path_on_cloud).download(path_local, filename)
