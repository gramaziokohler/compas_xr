import io
import json
import os

import pyrebase
from compas.data import json_dumps
from compas.data import json_loads

from compas_xr.storage.storage_interface import StorageInterface

try:
    # from urllib.request import urlopen
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


class Storage(StorageInterface):
    """
    A Storage is defined by a Firebase configuration path and a shared storage reference.

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
        self._ensure_storage()

    def _ensure_storage(self):
        """
        Ensures that the storage connection is established.
        If the connection is not yet established, it initializes it.
        If the connection is already established, it returns the existing connection.
        """
        if not Storage._shared_storage:
            path = self.config_path
            if not os.path.exists(path):
                raise Exception("Path Does Not Exist: {}".format(path))
            with open(path) as config_file:
                config = json.load(config_file)
            # TODO: Authorization for storage security (Works for now for us because our Storage is public)
            firebase = pyrebase.initialize_app(config)
            Storage._shared_storage = firebase.storage()

        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

    def _get_file_from_remote(self, url):
        """
        This function is used to get the information form the source url and returns a string
        It also checks if the data is None or == null (firebase return if no data)
        """
        try:
            get = urlopen(url).read().decode()
        except:
            raise Exception("unable to get file from url {}".format(url))

        if get is not None and get != "null":
            return get

        else:
            raise Exception("unable to get file from url {}".format(url))

    def construct_reference(self, cloud_file_name):
        """
        Constructs a storage reference for the specified cloud file name.

        Parameters
        ----------
        cloud_file_name : str
            The name of the cloud file.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Storage'
            The constructed storage reference.

        """
        return Storage._shared_storage.child(cloud_file_name)

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
        :class: 'pyrebase.pyrebase.Storage'
            The constructed storage reference.

        """
        return Storage._shared_storage.child(cloud_folder_name).child(cloud_file_name)

    def construct_reference_from_list(self, cloud_path_list):
        """
        Constructs a storage reference for consecutive cloud folders in list order.

        Parameters
        ----------
        cloud_path_list : list of str
            The list of cloud path names.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Storage'
            The constructed storage reference.

        """
        storage_reference = Storage._shared_storage
        for path in cloud_path_list:
            storage_reference = storage_reference.child(path)
        return storage_reference

    def get_data_from_reference(self, storage_reference):
        """
        Retrieves data from the specified storage reference.

        Parameters
        ----------
        storage_reference : pyrebase.pyrebase.Storage
            The storage reference pointing to the desired data.

        Returns
        -------
        data : dict or Compas Class Object
            The deserialized data retrieved from the storage reference.

        """
        url = storage_reference.get_url(token=None)
        data = self._get_file_from_remote(url)
        deserialized_data = json_loads(data)
        return deserialized_data

    def upload_bytes_to_reference_from_local_file(self, file_path, storage_reference):
        """
        Uploads data from bytes to the specified storage reference from a local file.

        Parameters
        ----------
        file_path : str
            The path to the local file.
        storage_reference : pyrebase.pyrebase.Storage
            The storage reference to upload the byte data to.

        Returns
        ------
        None

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        with open(file_path, "rb") as file:
            byte_data = file.read()
        storage_reference.put(byte_data)

    def upload_data_to_reference(self, data, storage_reference, pretty=True):
        """
        Uploads data to the specified storage reference.

        Parameters
        ----------
        data : Any should be json serializable
            The data to be uploaded.
        storage_reference : pyrebase.pyrebase.Storage
            The storage reference to upload the data to.
        pretty : bool, optional
            Whether to format the JSON data with indentation and line breaks (default is True).

        Returns
        ------
        None

        """
        serialized_data = json_dumps(data, pretty=pretty)
        file_object = io.BytesIO(serialized_data.encode())
        storage_reference.put(file_object)
