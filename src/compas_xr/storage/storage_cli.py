import os
import sys
import json
import io
from compas.data import Data
from compas.data import json_loads,json_dumps
from compas.datastructures import Assembly
from compas_xr.storage.storage_interface import StorageInterface
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
print("Are u really working?")

from Firebase.Auth import FirebaseAuthConfig
# from Firebase.Auth import FirebaseConfig
from Firebase.Auth import FirebaseAuthClient
from Firebase.Auth.Providers import FirebaseAuthProvider
from Firebase.Storage import FirebaseStorage
from Firebase.Storage import FirebaseStorageTask



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

def _event_trigger(event):
    print ("function is being called to trigger event and task was completed")
    event.set()


def _mre_event_trigger(task, mre):
    print ("entered mre function")

    if task.IsFaulted:
        print ("here")
    else:
        print ("This is a normal task")
        #TODO: THIS IS THE PROBLEM LINE
        # result = task.Result.Content
        mre.Set()
    
    # return result

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
                storage_client = FirebaseStorage(config["storageBucket"])
                print (storage_client)
                Storage._shared_storage = storage_client

        else:
            raise Exception("Path Does Not Exist: {}".format(path))

        # Still no storage? Fail, we can't do anything
        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

        return Storage._shared_storage
    
    
    def _start_async_call(self, fn, timeout=10):
        result = {}
        result["event"] = threading.Event()
        
        async_thread = threading.Thread(target=fn, args=(result, ))
        async_thread.start()
        async_thread.join(timeout=timeout)

        return result["data"]
    
    def download_file_from_remote(self, source, target, overwrite=True):
        """Download a file from a remote source and save it to a local destination.

        Parameters
        ----------
        source : str
            The url of the source file.
        target : str
            The path of the local destination.
        overwrite : bool, optional
            If True, overwrite `target` if it already exists.

        Examples
        --------
        .. code-block:: python

            import os
            import compas
            from compas.utilities.remote import download_file_from_remote

            source = 'https://raw.githubusercontent.com/compas-dev/compas/main/data/faces.obj'
            target = os.path.join(compas.APPDATA, 'data', 'faces.obj')

            download_file_from_remote(source, target)

        """
        parent = os.path.abspath(os.path.dirname(target))

        if not os.path.exists(parent):
            os.makedirs(parent)

        if not os.path.isdir(parent):
            raise Exception("The target path is not a valid file path: {}".format(target))

        if not os.access(parent, os.W_OK):
            raise Exception("The target path is not writable: {}".format(target))

        if not os.path.exists(target):
            urlretrieve(source, target)
        else:
            if overwrite:
                urlretrieve(source, target)
    
    def download_file(self, path_on_cloud, path_local):
        if Storage._shared_storage:
            # Shared storage instance with a specificatoin of file name.
            storage_refrence = Storage._shared_storage.Child(path_on_cloud)
            print (storage_refrence)

            def _begin_download(result):
                downloadurl_task = storage_refrence.GetDownloadUrlAsync()
                task_download = downloadurl_task.GetAwaiter()
                task_download.OnCompleted(lambda: result["event"].set())

                result["event"].wait()
                result["data"] = downloadurl_task.Result
            
            url = self._start_async_call(_begin_download)
            
            #THIS WORKED
            self.download_file_from_remote(url, path_local)
            print ("download_complete")

    def upload_file(self, path_on_cloud, path_local):
        if Storage._shared_storage:
            # Shared storage instance with a specification of file name.
            storage_refrence = Storage._shared_storage.Child(path_on_cloud)
            print (storage_refrence)

            
            with FileStream(path_local, FileMode.Open) as file_stream:
                
                print (type(file_stream))

                def _begin_upload(result):

                    uploadtask = storage_refrence.PutAsync(file_stream)
                    task_upload = uploadtask.GetAwaiter()
                    task_upload.OnCompleted(lambda: result["event"].set())

                    result["event"].wait()
                    result["data"] = True
                
                upload = self._start_async_call(_begin_upload)
           
                print (upload)

    def upload_assembly(self, path_on_cloud, assembly):
        if Storage._shared_storage:
            # Shared storage instance with a specification of file name.
            storage_refrence = Storage._shared_storage.Child(path_on_cloud)
                
            data = json_dumps(assembly, pretty=True)

            byte_data = Encoding.UTF8.GetBytes(data)
            stream = MemoryStream(byte_data)

            def _begin_upload(result):

                uploadtask = storage_refrence.PutAsync(stream)
                task_upload = uploadtask.GetAwaiter()
                task_upload.OnCompleted(lambda: result["event"].set())

                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
        
            print (upload)

    def download_assembly(self, path_on_cloud, path_local):
        if Storage._shared_storage:
            # Shared storage instance with a specificatoin of file name.
            storage_refrence = Storage._shared_storage.Child(path_on_cloud)
            print (storage_refrence)

            def _begin_download(result):
                downloadurl_task = storage_refrence.GetDownloadUrlAsync()
                task_download = downloadurl_task.GetAwaiter()
                task_download.OnCompleted(lambda: result["event"].set())

                result["event"].wait()
                result["data"] = downloadurl_task.Result
            
            url = self._start_async_call(_begin_download)
            
            #THIS WORKED -- Needs to be in an async event?
            download = self.download_file_from_remote(url, path_local)
            print ("download_complete")

            #TODO: This works, but I am not sure if there is a better way then download to a local and open the local... maybe download to MemoryStream or ByteArray?
            with open(path_local) as json_file:
                json_assembly = json.load(json_file)

            assembly_serialized = json_dumps(json_assembly)
            desearialized_data = json_loads(assembly_serialized)

            return desearialized_data

    def upload_data(self, path_on_cloud, data):
        if Storage._shared_storage:
            # Shared storage instance with a specification of file name.
            storage_refrence = Storage._shared_storage.Child(path_on_cloud)
           
            #Serialize data
            serialized_data = json_dumps(data)
            print (serialized_data)

            byte_data = Encoding.UTF8.GetBytes(serialized_data)
            stream = MemoryStream(byte_data)

            def _begin_upload(result):

                uploadtask = storage_refrence.PutAsync(stream)
                task_upload = uploadtask.GetAwaiter()
                task_upload.OnCompleted(lambda: result["event"].set())

                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
        
            print (upload)

    def download_data(self, path_on_cloud, path_local):
        if Storage._shared_storage:
            # Shared storage instance with a specificatoin of file name.
            storage_refrence = Storage._shared_storage.Child(path_on_cloud)
            print (storage_refrence)

            def _begin_download(result):
                downloadurl_task = storage_refrence.GetDownloadUrlAsync()
                task_download = downloadurl_task.GetAwaiter()
                task_download.OnCompleted(lambda: result["event"].set())

                result["event"].wait()
                result["data"] = downloadurl_task.Result
            
            url = self._start_async_call(_begin_download)
            
            #THIS WORKED -- Needs to be in an async event?
            download = self.download_file_from_remote(url, path_local)
            print ("download_complete")

            #TODO: This works, but I am not sure if there is a better way then download to a local and open the local... maybe download to MemoryStream or ByteArray?
            with open(path_local) as json_file:
                json_data = json.load(json_file)

            data_serialized = json_dumps(json_data)
            desearialized_data = json_loads(data_serialized)

            return desearialized_data

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
