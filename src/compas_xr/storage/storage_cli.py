import json
import os
import sys
import threading

import clr
from compas.data import json_dump
from compas.data import json_dumps
from compas.data import json_loads
from System.IO import File
from System.IO import FileMode
from System.IO import FileStream
from System.IO import MemoryStream
from System.Text import Encoding

from compas_xr.storage.storage_interface import StorageInterface

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

lib_dir = os.path.join(os.path.dirname(__file__), "dependencies")
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

clr.AddReference("Firebase.Auth.dll")
clr.AddReference("Firebase.dll")
clr.AddReference("Firebase.Storage.dll")

from Firebase.Auth import FirebaseAuthClient
from Firebase.Auth import FirebaseAuthConfig
from Firebase.Storage import FirebaseStorage

"""
TODO: add proper comments.
TODO: Review Function todo's
TODO: Authorization for Storage.
"""

class Storage(StorageInterface):
    
    _shared_storage = None

    def __init__(self, config_path):
        self.config_path = config_path
        self.storage = self._ensure_storage()

    #Internal Class Functions
    def _ensure_storage(self):
        # Initialize Firebase connection and storage only once
        if not Storage._shared_storage:
            path = self.config_path

            # Load the Firebase configuration file from the JSON file if the file exists
            if not os.path.exists(path):
                raise Exception("Path Does to config Not Exist: {}".format(path))
            with open(path) as config_file:
                config = json.load(config_file)

            #TODO: Authorization for storage security (Works for now for us because our Storage is public)
            #Initialize Storage from storage bucket
            storage_client = FirebaseStorage(config["storageBucket"])
            Storage._shared_storage = storage_client
            print ("Shared Storage Client Set")

        # Still no storage? Fail, we can't do anything
        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

        return Storage._shared_storage
    
    def _start_async_call(self, fn, timeout=10):
        """
        Manages asynchronous calls to the Storage.
        """
        result = {}
        result["event"] = threading.Event()
        async_thread = threading.Thread(target=fn, args=(result, ))
        async_thread.start()
        async_thread.join(timeout=timeout)
        return result["data"]
    
    def _get_file_from_remote(self, url):
        """
        This function is used to get the information form the source url and returns a string
        It also checks if the data is None or == null (firebase return if no data)
        """
        try:
            get = urlopen(url).read()

        except:
            raise Exception("unable to get file from url {}".format(url))
        
        if get is not None and get != "null":
            return get    
        
        else:
            raise Exception("unable to get file from url {}".format(url))

    #TODO: Same as RTDB: Can I turn this into a gloabal call back that can be used inside of every method?
    def _task_callback(task, result):
        task_awaiter = task.GetAwaiter()
        task_awaiter.OnCompleted(lambda: result["event"].set())
        result["event"].wait()
        result["data"] = True

    def construct_reference(self, cloud_file_name):
        return Storage._shared_storage.Child(cloud_file_name)

    def construct_reference_with_folder(self, cloud_folder_name, cloud_file_name):
        return Storage._shared_storage.Child(cloud_folder_name).Child(cloud_file_name)

    def construct_reference_from_list(self, cloud_path_list):
        storage_ref = Storage._shared_storage
        for path in cloud_path_list:
            storage_ref = storage_ref.Child(path)
        return storage_ref

    def upload_data_to_reference(self, data, storage_reference, pretty=True):
        self._ensure_storage()
        serialized_data = json_dumps(data, pretty=pretty)
        byte_data = Encoding.UTF8.GetBytes(serialized_data)
        stream = MemoryStream(byte_data)

        def _begin_upload(result):
            uploadtask = storage_reference.PutAsync(stream)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True

        self._start_async_call(_begin_upload)

    def upload_bytes_to_reference(self, byte_data, storage_reference):
        self._ensure_storage()
        bytes = Encoding.UTF8.GetBytes(byte_data)
        stream = MemoryStream(bytes)

        def _begin_upload(result):
            uploadtask = storage_reference.PutAsync(stream)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True

        self._start_async_call(_begin_upload)


    def get_data_from_reference(self, storage_refrence):
        self._ensure_storage()

        def _begin_download(result):
            downloadurl_task = storage_refrence.GetDownloadUrlAsync()
            task_download = downloadurl_task.GetAwaiter()
            task_download.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = downloadurl_task.Result
        
        url = self._start_async_call(_begin_download)
        data = self._get_file_from_remote(url)
        desearialized_data = json_loads(data)
        return desearialized_data

    #Functions for uploading .json and data
    def upload_file(self, path_on_cloud, path_local):
        self._ensure_storage()
        # Shared storage instance with a specification of file name.
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)

        if os.path.exists(path_local):

            with FileStream(path_local, FileMode.Open) as file_stream:

                def _begin_upload(result):

                    uploadtask = storage_refrence.PutAsync(file_stream)
                    task_upload = uploadtask.GetAwaiter()
                    task_upload.OnCompleted(lambda: result["event"].set())

                    result["event"].wait()
                    result["data"] = True
                
                upload = self._start_async_call(_begin_upload)
            
        else:
            raise Exception("path does not exist {}".format(path_local))
 


    # def upload_data(self, path_on_cloud, data):
        
    #     self._ensure_storage()
        
    #     # Shared storage instance with a specification of file name.
    #     storage_refrence = Storage._shared_storage.Child(path_on_cloud)
        
    #     #Serialize data
    #     serialized_data = json_dumps(data)

    #     byte_data = Encoding.UTF8.GetBytes(serialized_data)
    #     stream = MemoryStream(byte_data)

    #     def _begin_upload(result):

    #         uploadtask = storage_refrence.PutAsync(stream)
    #         task_upload = uploadtask.GetAwaiter()
    #         task_upload.OnCompleted(lambda: result["event"].set())

    #         result["event"].wait()
    #         result["data"] = True

    #     self._start_async_call(_begin_upload)

    #Download Functions
    # def download_file(self, path_on_cloud, path_local):
        
    #     self._ensure_storage()
        
    #     storage_refrence = Storage._shared_storage.Child(path_on_cloud)

    #     def _begin_download(result):
    #         downloadurl_task = storage_refrence.GetDownloadUrlAsync()
    #         task_download = downloadurl_task.GetAwaiter()
    #         task_download.OnCompleted(lambda: result["event"].set())

    #         result["event"].wait()
    #         result["data"] = downloadurl_task.Result
        
    #     url = self._start_async_call(_begin_download)
        
    #     data = self._get_file_from_remote(url)

    #     if os.path.exists(path_local):
    #         #TODO: Pretty is not working and I do not know why.
    #         json_dump(data, path_local, pretty= True)
        
    #     else:
    #         raise Exception("path does not exist {}".format(path_local))
    #     print ("file downloaded")

    # def get_data(self, path_on_cloud):
        
    #     self._ensure_storage()
        
    #     # Shared storage instance with a specificatoin of file name.
    #     storage_refrence = Storage._shared_storage.Child(path_on_cloud)

    #     def _begin_download(result):
    #         downloadurl_task = storage_refrence.GetDownloadUrlAsync()
    #         task_download = downloadurl_task.GetAwaiter()
    #         task_download.OnCompleted(lambda: result["event"].set())
    #         result["event"].wait()
    #         result["data"] = downloadurl_task.Result
        
    #     url = self._start_async_call(_begin_download)
    #     data = self._get_file_from_remote(url)
    #     desearialized_data = json_loads(data)

    #     return desearialized_data

    #Manage Objects - .obj upload options
    def upload_obj(self, path_on_cloud, cloud_folder, path_local):
        self._ensure_storage()
        storage_refrence = Storage._shared_storage.Child("obj_storage").Child(cloud_folder).Child(path_on_cloud)

        if os.path.exists(path_local):
            
            data = File.ReadAllBytes(path_local)
            stream = MemoryStream(data)

            def _begin_upload(result):

                uploadtask = storage_refrence.PutAsync(stream)
                task_upload = uploadtask.GetAwaiter()
                task_upload.OnCompleted(lambda: result["event"].set())

                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
            print ("obj uploaded")
        
        else:
            raise Exception("path does not exist {}".format(path_local))

    def upload_objs(self, cloud_folder_name, folder_local): #TODO: THIS SHOULD ALSO GO TO PROJECT MANAGER
        
        self._ensure_storage()
                    
        if os.path.exists(folder_local) and os.path.isdir(folder_local):
            
            file_info = []

            for f in os.listdir(folder_local):
                file_path = os.path.join(folder_local, f)
                if os.path.isfile(file_path):
                    file_info.append((file_path, f))

            for path, name in file_info:

                if os.path.exists(path):
                    #TODO: Call upload obj as an internal method.
                    """
                    Also works with the function call below, but not sure if this is the best idea
                    # self.upload_obj(name, cloud_folder_name, path)
                    """
                    data = File.ReadAllBytes(path)
                    stream = MemoryStream(data)

                    def _begin_upload(result):
                        storage_refrence = Storage._shared_storage.Child("obj_storage").Child(cloud_folder_name).Child(name)
                        uploadtask = storage_refrence.PutAsync(stream)
                        task_upload = uploadtask.GetAwaiter()
                        task_upload.OnCompleted(lambda: result["event"].set())

                        result["event"].wait()
                        result["data"] = True

                    upload = self._start_async_call(_begin_upload)
                
                else:
                    raise Exception("path does not exist {}".format(path))

            print ("obj's uploaded")

        else:
            raise Exception("path does not exist {}".format(folder_local))
