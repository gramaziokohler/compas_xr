import os
import sys
import json
from compas.data import Data
from compas_xr.realtime_database.realtime_database_interface import RealtimeDatabaseInterface
import clr
import threading
from System.IO import FileStream, FileMode, MemoryStream, Stream
from System.Text import Encoding
from System.Threading import (
    ManualResetEventSlim,
    CancellationTokenSource,
    CancellationToken)
try:
    # from urllib.request import urlopen
    from urllib.request import urlretrieve
except ImportError:
    # from urllib2 import urlopen
    from urllib import urlretrieve


lib_dir = os.path.join(os.path.dirname(__file__), "dependencies")
print (lib_dir)
if lib_dir not in sys.path:
    sys.path.append(lib_dir)


clr.AddReference("Firebase.Auth.dll")
clr.AddReference("Firebase.dll")
clr.AddReference("Firebase.Storage.dll")
print("Are u really working realtime?")

from Firebase.Database import FirebaseClient
# from Firebase.Auth import FirebaseAuthConfig
# # from Firebase.Auth import FirebaseConfig
# from Firebase.Auth import FirebaseAuthClient
# from Firebase.Auth.Providers import FirebaseAuthProvider
# from Firebase.Storage import FirebaseStorage


#TODO: Update file path... this currently maps to C: drive or wherever the program is running the code... this is important.
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

class RealtimeDatabase(RealtimeDatabaseInterface):

    # Class attribute for the shared firebase database reference
    _shared_database = None
    
    # def __init__(self, config_path = None):
        
    #     pass
    
    def __init__(self, config_path = None):
        
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        # self.auth_client = None
        # self.storage_client = None
        self.database = self._ensure_database()

    def _ensure_database(self):

        # Initialize Firebase connection and databse only once
        if not RealtimeDatabase._shared_database:
            path = self.config_path
            print ("This is your path" + path)

            # Load the Firebase configuration file from the JSON file if the file exists
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)

                # Initialize Firebase authentication and storage
                # api_key = config["apiKey"]
                # auth_config_test = FirebaseAuthConfig()
                # auth_config = FirebaseAuthProvider(FirebaseConfig(api_key))
                # auth_config.api_key = config["apiKey"]  # Set the API key separately
                # auth_client = FirebaseAuthClient(config_file)

                #Initilize Storage instance from storageBucket
                database_client = FirebaseClient(config["databaseURL"])
                print (database_client)
                RealtimeDatabase._shared_database = database_client

        else:
            raise Exception("Path Does Not Exist: {}".format(path))

        # Still no storage? Fail, we can't do anything
        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize storage!")

        return RealtimeDatabase._shared_database
