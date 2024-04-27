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
    """
    A Storage Class is defined by a Firebase configuration path and a shared storage reference.

    The Storage class is responsible for initializing and managing the connection to a Firebase Storage.
    It ensures that the storage connection is established only once and shared across all instances of the class.

    Parameters
    ----------
    config_path : str
        The path to the Firebase configuration JSON file.

    Attributes
    ----------
    config_path : str
        The path to the Firebase configuration JSON file.
    _shared_storage : pyrebase.Storage, class attribute
        The shared pyrebase.Storage instance representing the connection to the Firebase Storage.
    """

    _shared_storage = None

    def __init__(self, config_path):
        self.config_path = config_path
        self.storage = self._ensure_storage()

    def _ensure_storage(self):
        """
        Ensures that the storage connection is established.
        If the connection is not yet established, it initializes it.
        If the connection is already established, it returns the existing connection.
        """
        if not Storage._shared_storage:
            path = self.config_path
            if not os.path.exists(path):
                raise Exception("Path Does to config Not Exist: {}".format(path))
            with open(path) as config_file:
                config = json.load(config_file)
            # TODO: Authorization for storage security (Works for now for us because our Storage is public)
            storage_client = FirebaseStorage(config["storageBucket"])
            Storage._shared_storage = storage_client

        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

        return Storage._shared_storage

    def _start_async_call(self, fn, timeout=10):
        """
        Manages asynchronous calls to the Storage.
        """
        result = {}
        result["event"] = threading.Event()
        async_thread = threading.Thread(target=fn, args=(result,))
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

    # TODO: Same as RTDB: Can I turn this into a gloabal call back that can be used inside of every method?
    def _task_callback(task, result):
        task_awaiter = task.GetAwaiter()
        task_awaiter.OnCompleted(lambda: result["event"].set())
        result["event"].wait()
        result["data"] = True

    def construct_reference(self, cloud_file_name):
        """
        Constructs a storage reference for the specified cloud file name.

        Parameters
        ----------
        cloud_file_name : str
            The name of the cloud file.

        Returns
        -------
        :class: 'Firebase.Storage.FirebaseStorageReference'
            The constructed storage reference.

        """
        return Storage._shared_storage.Child(cloud_file_name)

    def construct_reference_with_folder(self, cloud_folder_name, cloud_file_name):
        """
        Constructs a storage reference for the specified cloud folder name and file name.

        Parameters
        ----------
        cloud_folder_name : str
            The name of the cloud folder.
        cloud_file_name : str
            The name of the cloud file.

        Returns
        -------
        :class: 'Firebase.Storage.FirebaseStorageReference'
            The constructed storage reference.

        """
        return Storage._shared_storage.Child(cloud_folder_name).Child(cloud_file_name)

    def construct_reference_from_list(self, cloud_path_list):
        """
        Constructs a storage reference for consecutive cloud folders in list order.

        Parameters
        ----------
        cloud_path_list : list of str
            The list of cloud path names.

        Returns
        -------
        :class: 'Firebase.Storage.FirebaseStorageReference'
            The constructed storage reference.

        """
        storage_ref = Storage._shared_storage
        for path in cloud_path_list:
            storage_ref = storage_ref.Child(path)
        return storage_ref

    def get_data_from_reference(self, storage_refrence):
        """
        Retrieves data from the specified storage reference.

        Parameters
        ----------
        storage_reference : Firebase.Storage.FirebaseStorageReference
            The storage reference pointing to the desired data.

        Returns
        -------
        data : dict or Compas Class Object
            The deserialized data retrieved from the storage reference.

        """
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

    def upload_bytes_to_reference_from_local_file(self, file_path, storage_reference):
        """
        Uploads data from bytes to the specified storage reference from a local file.

        Parameters
        ----------
        file_path : str
            The path to the local file.
        storage_reference : Firebase.Storage.FirebaseStorageReference
            The storage reference to upload the byte data to.

        Returns
        ------
        None

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        self._ensure_storage()
        byte_data = File.ReadAllBytes(file_path)
        stream = MemoryStream(byte_data)

        def _begin_upload(result):
            uploadtask = storage_reference.PutAsync(stream)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True

        self._start_async_call(_begin_upload)

    def upload_data_to_reference(self, data, storage_reference, pretty=True):
        """
        Uploads data to the specified storage reference.

        Parameters
        ----------
        data : Any should be json serializable
            The data to be uploaded.
        storage_reference : Firebase.Storage.FirebaseStorageReference
            The storage reference to upload the data to.
        pretty : bool, optional
            Whether to format the JSON data with indentation and line breaks (default is True).

        Returns
        ------
        None

        """
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
