import pyrebase
import json
import os
from compas.data import Data
from compas_xr.storage.storage_interface import StorageInterface
# from compas_xr import SCRIPT

# Get the current file path
CURRENT_FILE_PATH = os.path.abspath(__file__)

# Define the number of levels to navigate up
LEVELS_TO_GO_UP = 4

#Construct File path to the correct location
PARENT_FOLDER = os.path.abspath(os.path.join(CURRENT_FILE_PATH, "../" * LEVELS_TO_GO_UP))

# Enter another folder
TARGET_FOLDER = os.path.join(PARENT_FOLDER, "scripts")
DEFAULT_CONFIG_PATH = os.path.join(TARGET_FOLDER, "firebase_config.json")


class Storage(StorageInterface, Data):

    # Class attribute for the shared firebase storage reference
    _shared_storage = None

    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self._guid = None
        print("Creating instance")
        self._ensure_storage()

    def _ensure_storage(self):
        # Initialize firebase connection and storage only once
        if not Storage._shared_storage:
            path = self.config_path #or self.default_config_path

            # Load the firebase configuration file from the JSON file if file exists.
            if os.path.exists(path):
                print(path)
                with open(path) as config_file:
                    config = json.load(config_file)

            else:
                raise Exception("Path Does Not Exist: {}".format(path))

            firebase = pyrebase.initialize_app(config)
            Storage._shared_storage = firebase.storage()

        # Still no storage? Fail, we can't do anything
        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

    def upload_file(self, path_on_cloud, path_local):
        self._ensure_storage()
        Storage._shared_storage.child(path_on_cloud).put(path_local)

    def download_file(self, path_on_cloud, path_local):
        self._ensure_storage()
        filename = path_local
        Storage._shared_storage.child(path_on_cloud).download(path_local, filename)

    @property
    def data(self):
        return dict(config_path=self.config_path)

    @data.setter
    def data(self, value):
        self.config_path = value["config_path"]

    @classmethod
    def from_data(cls, data):
        config_path = data["config_path"]
        return cls(config_path)
