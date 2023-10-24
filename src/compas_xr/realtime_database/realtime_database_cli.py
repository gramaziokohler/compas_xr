import os
import sys
import json
from compas.data import json_dumps,json_loads
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
from Firebase.Database.Query import FirebaseQuery
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

    def _start_async_call(self, fn, timeout=10):
        print ("inside of start async")
        result = {}
        result["event"] = threading.Event()
        
        async_thread = threading.Thread(target=fn, args=(result, ))
        async_thread.start()
        async_thread.join(timeout=timeout)

        return result["data"]
    
    def upload_file_all(self, json_path, parentname):
        
        if RealtimeDatabase._shared_database:

            with open(json_path) as json_file:
                json_data = json.load(json_file)
            
            serialized_data = json_dumps(json_data)
            database_reference = RealtimeDatabase._shared_database 

            def _begin_upload(result):
                print ("inside of begin upload")
                uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
                print (uploadtask)
                task_upload = uploadtask.GetAwaiter()
                print (task_upload)
                task_upload.OnCompleted(lambda: result["event"].set())
                print
                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
            print (upload)

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")
    
    
    def upload_file(self, json_path, parentname, paramaters):
        
        if RealtimeDatabase._shared_database:

            with open(json_path) as json_file:
                json_data = json.load(json_file)
            
            paramaters_list = {}

            for param in paramaters:
                values = json_data[param]
                paramaters_dict = {param: values}
                paramaters_list.update(paramaters_dict)
            
            # print (type(paramaters_list))
            # print (type(paramaters_list[0]))

            serialized_data = json_dumps(paramaters_list)
            database_reference = RealtimeDatabase._shared_database 

            def _begin_upload(result):
                print ("inside of begin upload")
                uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
                print (uploadtask)
                task_upload = uploadtask.GetAwaiter()
                print (task_upload)
                task_upload.OnCompleted(lambda: result["event"].set())
                print
                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
            print (upload)

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")

    def upload_file_all_as_child(self, json_path, parentname, childname):
        
        if RealtimeDatabase._shared_database:

            with open(json_path) as json_file:
                json_data = json.load(json_file)
            
            serialized_data = json_dumps(json_data)
            database_reference = RealtimeDatabase._shared_database
            print (type(database_reference))
            parent_reference = database_reference.Child(parentname)
            print (type(parent_reference))
            parent_query = FirebaseQuery(parent_reference, database_reference)
            print (parent_reference)

            def _begin_upload(result):
                print ("inside of begin upload")
                uploadtask = parent_query.Child(childname).PutAsync(serialized_data)
                print (uploadtask)
                task_upload = uploadtask.GetAwaiter()
                print (task_upload)
                task_upload.OnCompleted(lambda: result["event"].set())
                print
                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
            print (upload)

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")
