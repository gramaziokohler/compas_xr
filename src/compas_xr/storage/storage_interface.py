import json
import os
from copy import deepcopy

from compas.data import json_dump


class StorageInterface(object):
    """
    The StorageInterface class serves as the shared interface for Storage classes that
    operate in IronPython and Python 3.0.

    Methods within this class are designed to rely on shared interfaces that are implemented in child classes.
    """

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

    def upload_bytes_to_reference_from_local_file(self, file_path, storage_reference):
        raise NotImplementedError("Implemented on child classes")

    def upload_data(self, data, cloud_file_name, pretty=True):
        """
        Uploads data to the Firebase Storage under specified cloud file name.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        cloud_file_name : str
            The name of the reference under which the data will be stored file type should be specified.(ex: .json)
        pretty : bool, optional
            A boolean that determines if the data should be formatted for readability. Default is True.

        Returns
        -------
        None

        """
        storage_reference = self.construct_reference(cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_from_json(self, path_local, pretty=True):
        """
        Uploads data to the Firebase Storage from JSON file.

        Parameters
        ----------
        path_local : str (path)
            The local path at which the JSON file is stored.
        pretty : bool, optional
            A boolean that determines if the data should be formatted for readability. Default is True.

        Returns
        -------
        None

        """
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as file:
            data = json.load(file)
        cloud_file_name = os.path.basename(path_local)
        storage_reference = self.construct_reference(cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_to_folder(self, data, cloud_folder_name, cloud_file_name, pretty=True):
        """
        Uploads data to the Firebase Storage under specified cloud folder name in cloud file name.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        cloud_folder_name : str
            The name of the folder under which the data will be stored.
        cloud_file_name : str
            The name of the reference under which the data will be stored file type should be specified.(ex: .json)
        pretty : bool, optional
            A boolean that determines if the data should be formatted for readability. Default is True.

        Returns
        -------
        None

        """
        storage_reference = self.construct_reference_with_folder(cloud_folder_name, cloud_file_name)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_data_to_deep_reference(self, data, cloud_path_list, pretty=True):
        """
        Uploads data to the Firebase Storage under specified reference names in list order.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        cloud_path_list : list of str
            The list of reference names under which the data will be stored file type should be specified.(ex: .json)
        pretty : bool, optional
            A boolean that determines if the data should be formatted for readability. Default is True.

        Returns
        -------
        None

        """
        storage_reference = self.construct_reference_from_list(cloud_path_list)
        self.upload_data_to_reference(data, storage_reference, pretty)

    def upload_file_as_bytes(self, file_path):
        """
        Uploads a file as bytes to the Firebase Storage.

        Parameters
        ----------
        file_path : str
            The local path of the file to be uploaded.

        Returns
        -------
        None

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        file_name = os.path.basename(file_path)
        storage_reference = self.construct_reference(file_name)
        self.upload_bytes_to_reference_from_local_file(file_path, storage_reference)

    def upload_file_as_bytes_to_deep_reference(self, file_path, cloud_path_list):
        """
        Uploads a file as bytes to the Firebase Storage to specified cloud path.

        Parameters
        ----------
        file_path : str
            The local path of the file to be uploaded.
        cloud_path_list : list of str
            The list of reference names under which the file will be stored.

        Returns
        -------
        None

        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found: {}".format(file_path))
        file_name = os.path.basename(file_path)
        new_path_list = deepcopy(cloud_path_list)
        new_path_list.append(file_name)
        print("new_path_list: {}".format(new_path_list))
        storage_reference = self.construct_reference_from_list(new_path_list)
        self.upload_bytes_to_reference_from_local_file(file_path, storage_reference)

    def upload_files_as_bytes_from_directory_to_deep_reference(self, directory_path, cloud_path_list):
        """
        Uploads all files in specified directory as bytes to the Firebase Storage at specified cloud path in list order.

        Parameters
        ----------
        directory_path : str
            The local path of the directory in which files are stored.
        cloud_path_list : list of str
            The list of reference names under which the file will be stored.

        Returns
        -------
        None

        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            raise FileNotFoundError("Directory not found: {}".format(directory_path))
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            print("Uploading file: {}".format(file_path))
            print("To cloud path: {}".format(cloud_path_list))
            self.upload_file_as_bytes_to_deep_reference(file_path, cloud_path_list)

    # TODO: This works as it should, but I have a lot of problems with json_loads
    def get_data(self, cloud_file_name):
        """
        Retrieves data from the Firebase Storage for specified cloud file name.

        Parameters
        ----------
        cloud_file_name : str
            The name of the cloud file.

        Returns
        -------
        data : dict or Compas Class Object
            The retrieved data in dictionary format or as Compas Class Object.

        """
        storage_reference = self.construct_reference(cloud_file_name)
        return self.get_data_from_reference(storage_reference)

    # TODO: This is not working... for some reason the GetDownloadUrlAsync always results Faulted
    def get_data_from_folder(self, cloud_folder_name, cloud_file_name):
        """
        Retrieves data from the Firebase Storage for specified cloud folder name and cloud file name.

        Parameters
        ----------
        cloud_folder_name : str
            The name of the cloud folder.
        cloud_file_name : str
            The name of the cloud file.

        Returns
        -------
        data : dict or Compas Class Object
            The retrieved data in dictionary format or as Compas Class Object.

        """
        storage_reference = self.construct_reference_with_folder(cloud_folder_name, cloud_file_name)
        return self.get_data_from_reference(storage_reference)

    # TODO: This is not working... for some reason the GetDownloadUrlAsync always results Faulted
    def get_data_from_deep_reference(self, cloud_path_list):
        """
        Retrieves data from the Firebase Storage for specified cloud folder name and cloud file name.

        Parameters
        ----------
        cloud_folder_name : str
            The name of the cloud folder.
        cloud_file_name : str
            The name of the cloud file.

        Returns
        -------
        data : dict or Compas Class Object
            The retrieved data in dictionary format or as Compas Class Object.

        """
        storage_reference = self.construct_reference_from_list(cloud_path_list)
        return self.get_data_from_reference(storage_reference)

    # TODO: This worked with Frame.__data__ but not with TimberAssembly.__data__
    def download_data_to_json(self, cloud_file_name, path_local, pretty=True):
        """
        Downloads data from the Firebase Storage for specified cloud file name.

        Parameters
        ----------
        cloud_file_name : str
            The name of the cloud file.
        path_local : str (path)
            The local path at which the JSON file will be stored.
        pretty : bool, optional
            A boolean that determines if the data should be formatted for readability. Default is True.

        Returns
        -------
        None

        """
        data = self.get_data(cloud_file_name)
        directory_name = os.path.dirname(path_local)
        if not os.path.exists(directory_name):
            print("Directory {} does not exist!".format(directory_name))
        json_dump(data=data, fp=path_local, pretty=pretty)
