import pyrebase
import json
import os
from compas.data import Data, json_dumps, json_loads
from compas_xr.storage.storage_interface import StorageInterface

try:
    # from urllib.request import urlopen
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

class Storage(StorageInterface):

    # Class attribute for the shared firebase storage reference
    _shared_storage = None

    def __init__(self, config_path=None):
        self.config_path = config_path
        self._guid = None
        self._ensure_storage()

    #Internal Class functions
    def _ensure_storage(self):
        # Initialize firebase connection and storage only once
        if not Storage._shared_storage:
            path = self.config_path

            # Load the firebase configuration file from the JSON file if file exists.
            if os.path.exists(path):
                print(path)
                with open(path) as config_file:
                    config = json.load(config_file)

            else:
                raise Exception("Path Does Not Exist: {}".format(path))

            #TODO: Authorization for storage security (Works for now for us because our Storage is public)
            
            firebase = pyrebase.initialize_app(config)
            Storage._shared_storage = firebase.storage()

        # Still no storage? Fail, we can't do anything
        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

    def _get_file_from_remote(self, url):
        
        """
        This function is used to get the information form the source url and returns a string
        It also checks if the data is None or == null (firebase return if no data)
        """

        try:
            get = urlopen(url).readline().decode()

        except:
            raise Exception("unable to get file from url {}".format(url))
        
        if get is not None and get != "null":
            return get    
        
        else:
            raise Exception("unable to get file from url {}".format(url))
    
    #Functions for uploading datatypes to Firebase Storage
    def upload_file(self, path_on_cloud, path_local):
        self._ensure_storage()
        Storage._shared_storage.child(path_on_cloud).put(path_local)

    def upload_data(self, path_on_cloud, data):
        #Check Storage Refrence
        self._ensure_storage()

        #Serialize data
        serialized_data = json_dumps(data)

        Storage._shared_storage.child(path_on_cloud).put(serialized_data)

    #Functions for downloading datatypes from Firebase Storage
    def download_file(self, path_on_cloud, path_local):
        self._ensure_storage()
        
        filename = path_local
        Storage._shared_storage.child(path_on_cloud).download(path_local, filename)
    
    def get_data(self, path_on_cloud):
        #Check Storage Reference
        self._ensure_storage()
        
        url = Storage._shared_storage.child(path_on_cloud).get_url(token=None)
        
        data = self._get_file_from_remote(url)

        # Deserialize data
        desearlize_data = json_loads(data)
        
        return desearlize_data
    
    #Manage Objects - .obj upload options
    def upload_obj(self, path_on_cloud, cloud_folder, path_local):
        self._ensure_storage()

        storage_reference = Storage._shared_storage.child("obj_storage").child(cloud_folder)

        if os.path.exists(path_local):
            
            with open(path_local, 'rb') as file:
                data = file.read()

            upload = storage_reference.child(path_on_cloud).put(data)

        else:
            raise Exception("path does not exist {}".format(path_local))
    
    def upload_objs(self, folder_local, cloud_folder_name):

        self._ensure_storage()

        storage_reference = Storage._shared_storage.child("obj_storage").child(cloud_folder_name)

        if os.path.exists(folder_local) and os.path.isdir(folder_local):
            
            file_info = []
            
            for f in os.listdir(folder_local):
                file_path = os.path.join(folder_local, f)
                if os.path.isfile(file_path):
                    file_info.append((file_path, f))

            for path, name in file_info:

                if os.path.exists(path):
                    with open(path, 'rb') as file:
                        data = file.read()

                    upload = storage_reference.child(name).put(data)

                else:
                    raise Exception("path does not exist {}".format(path))
        
        else:
            raise Exception("path does not exist {}".format(folder_local))

