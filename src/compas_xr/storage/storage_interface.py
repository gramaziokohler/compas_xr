import json
import os

from compas.data import json_dump, json_loads
from System.IO import File
class StorageInterface(object):

    def construct_reference(self, cloud_file_name):
        raise NotImplementedError("Implemented on child classes")

    def construct_reference_with_folder(self, cloud_folder_name, cloud_file_name):
        raise NotImplementedError("Implemented on child classes")

    def construct_reference_from_list(self, cloud_path_list):
        raise NotImplementedError("Implemented on child classes")

    def upload_data_to_reference(self, data, storage_reference, pretty=True):
        raise NotImplementedError("Implemented on child classes")
    
    def get_data_from_reference(self, storage_refrence):
        raise NotImplementedError("Implemented on child classes")

    def upload_data(self, data, cloud_file_name, pretty=True):
        storage_reference = self.construct_reference(cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_bytes_to_reference(self, byte_data, storage_reference):
        raise NotImplementedError("Implemented on child classes")

    def upload_data_from_json(self, path_local, cloud_file_name, pretty=True): #TODO: THIS SHOULD NOT HAVE A NAME INPUT. (ERROR PRONE)
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as file:
            data = json.load(file)
        storage_reference = self.construct_reference(cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_to_folder(self, data, cloud_folder_name, cloud_file_name, pretty=True):
        storage_reference = self.construct_reference_with_folder(cloud_folder_name, cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_to_deep_reference(self, data, cloud_path_list, pretty=True):
        storage_reference = self.construct_reference_from_list(cloud_path_list)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def get_data(self, cloud_file_name):
        storage_reference = self.construct_reference(cloud_file_name)
        return self.get_data_from_reference(storage_reference)
    
    def upload_obj(self, path_on_cloud, cloud_folder, path_local):
        return NotImplementedError("Implemented on child classes")

    def upload_file_from_bytes(self, file_path):
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        with open(file_path, 'rb') as file:
            byte_data = file.read()
        print(type(byte_data))
        file_name = os.path.basename(file_path)
        storage_reference = self.construct_reference(file_name)
        self.upload_bytes_to_reference(byte_data, storage_reference)

    #TODO: This is not working... for some reason the GetDownloadUrlAsync always results Faulted
    def get_data_from_folder(self, cloud_folder_name, cloud_file_name):
        storage_reference = self.construct_reference_with_folder(cloud_folder_name, cloud_file_name)
        print(storage_reference)
        return self.get_data_from_reference(storage_reference)

    #TODO: This is not working... for some reason the GetDownloadUrlAsync always results Faulted
    def get_data_from_deep_reference(self, cloud_path_list):
        storage_reference = self.construct_reference_from_list(cloud_path_list)
        return self.get_data_from_reference(storage_reference)

    #TODO: This worked with Frame.__data__ but not with TimberAssembly.__data__
    def download_data_to_file(self, cloud_file_name, path_local, pretty=True):
        data = self.get_data(cloud_file_name)
        directory_name = os.path.dirname(path_local)
        if not os.path.exists(directory_name):
            print("Directory {} does not exist!".format(directory_name))
        json_dump(data=data, fp=path_local, pretty=pretty)
