import os
import sys
import json
from compas.data import Data
from compas_xr.storage.storage_interface import StorageInterface
import clr
import threading
import time

#TODO: Find correct dependencies (these two for example)
lib_dir = os.path.join(os.path.dirname(__file__), "dependencies")
print (lib_dir)
if lib_dir not in sys.path:
    sys.path.append(lib_dir)


#TODO: Find correct dependencies (these two for example)
# clr.AddReference("LiteDB.dll")
clr.AddReference("Firebase.Auth.dll")
clr.AddReference("Firebase.dll")
clr.AddReference("Firebase.Storage.dll")
print("Are u really working?")

from Firebase.Auth import FirebaseAuthConfig
# from Firebase.Auth import FirebaseConfig
from Firebase.Auth import FirebaseAuthClient
from Firebase.Auth.Providers import FirebaseAuthProvider
from Firebase.Storage import FirebaseStorage
from Firebase.Storage import FirebaseStorageTask
from System.IO import FileStream, FileMode
from System.Threading import CancellationTokenSource


#TODO: Update file path... this currently maps to C: drive or wherever the program is running the code
# Get the current file path
CURRENT_FILE_PATH = os.path.abspath(__file__)
# print (CURRENT_FILE_PATH)

# Define the number of levels to navigate up
LEVELS_TO_GO_UP = 4

#Construct File path to the correct location
PARENT_FOLDER = os.path.abspath(os.path.join(CURRENT_FILE_PATH, "../" * LEVELS_TO_GO_UP))

# Enter another folder
TARGET_FOLDER = os.path.join(PARENT_FOLDER, "scripts")
DEFAULT_CONFIG_PATH = os.path.join(TARGET_FOLDER, "firebase_config.json")

class Storage(StorageInterface):
    
    _shared_storage = None

    def __init__(self, config_path = None):
        
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        # self.auth_client = None
        # self.storage_client = None
        self.storage = self._ensure_storage()

    def _ensure_storage(self):
    # Initialize Firebase connection and storage only once
        if not Storage._shared_storage:
            path = self.config_path # Replace with the path to your config JSON file
            print ("This is your path" + path)

            # Load the Firebase configuration file from the JSON file if the file exists
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)
                
                print ("I entered here")

                # Initialize Firebase authentication and storage
                # api_key = config["apiKey"]
                # auth_config_test = FirebaseAuthConfig()
                # auth_config = FirebaseAuthProvider(FirebaseConfig(api_key))
                # auth_config.api_key = config["apiKey"]  # Set the API key separately
                # auth_client = FirebaseAuthClient(config_file)

                #Initilize Storage instance from storageBucket
                storage_client = FirebaseStorage(config["storageBucket"])
                print (storage_client)
                Storage._shared_storage = storage_client

        else:
            raise Exception("Path Does Not Exist: {}".format(path))

        # Still no storage? Fail, we can't do anything
        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

        return Storage._shared_storage
    
    
    def download_file(self, path_on_cloud, path_local):
        if Storage._shared_storage:
            # Use the Firebase.Storage library to upload the file
            storage_refrence = Storage._shared_storage.Child(path_on_cloud)
            print (storage_refrence)




    def upload_file(self, path_on_cloud, path_local):
        if Storage._shared_storage:
            # Use the Firebase.Storage library to upload the file
            storage_refrence = Storage._shared_storage.Child(path_on_cloud)
            print (storage_refrence)

            event = threading.Event()

            def cont():
                print ("function is being called to trigger event and task was completed")
                event.set()

            with FileStream(path_local, FileMode.Open) as file_stream:
                
                task = storage_refrence.PutAsync(file_stream)
                task_thing = task.GetAwaiter()
                task_thing.OnCompleted(cont)
                event.wait(3.0)
                
                print (task)



# # Back up PROXY option, and works but not the ideal solution.
# from compas.rpc import Proxy

# class Storage(StorageInterface):
#     def __init__(self, config_file):
#         self.config_file = config_file

#     def download_file(self, path_on_cloud, path_local):
#         st = Proxy('compas_xr.storage.storage_proxy_api')
#         st.download_file(path_on_cloud, path_local, self.config_file)

#     def upload_file(self, path_on_cloud, path_local):
#         st = Proxy('compas_xr.storage.storage_proxy_api')
#         st.upload_file(path_on_cloud, path_local, self.config_file)
