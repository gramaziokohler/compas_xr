import json
import os

from compas_timber.assembly import TimberAssembly


class RealtimeDatabaseInterface(object):
    """
    The RealtimeDatabaseInterface class serves as the shared interface for RealtimeDatabase classes that
    operate in IronPython and Python 3.0.

    Methods within this class are designed to rely on shared interfaces that are implemented in child classes.
    """

    def construct_reference(self, parentname):
        raise NotImplementedError("Implemented on child classes")

    def construct_child_refrence(self, parentname, childname):
        raise NotImplementedError("Implemented on child classes")

    def construct_grandchild_refrence(self, parentname, childname, grandchildname):
        raise NotImplementedError("Implemented on child classes")

    def construct_reference_from_list(self, reference_list):
        raise NotImplementedError("Implemented on child classes")

    def upload_data_to_reference(self, data, database_reference):
        raise NotImplementedError("Implemented on child classes")

    def get_data_from_reference(self, database_reference):
        raise NotImplementedError("Implemented on child classes")

    def delete_data_from_reference(self, database_reference):
        raise NotImplementedError("Implemented on child classes")

    def stream_data_from_reference(self, callback, database_reference):
        raise NotImplementedError("Implemented on child classes")

    def upload_data(self, data, reference_name):
        """
        Uploads data to the Firebase Realtime Database under specified reference name.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        reference_name : str
            The name of the reference under which the data will be stored.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference(reference_name)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_to_reference_as_child(self, data, reference_name, child_name):
        """
        Uploads data to the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        reference_name : str
            The name of the reference under which the child should exist.
        child_name : str
            The name of the reference under which the data will be stored.

        Returns
        -------
        None

        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_to_deep_reference(self, data, reference_list):
        """
        Uploads data to the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        reference_list : list of str
            The names in sequence order in which the data should be nested for upload.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference_from_list(reference_list)
        self.upload_data_to_reference(data, database_reference)

    def upload_data_from_file(self, path_local, refernce_name):
        """
        Uploads data to the Firebase Realtime Database under specified reference name from a file.

        Parameters
        ----------
        path_local : str
            The local path in which the data is stored as a json file.
        reference_name : str
            The name of the reference under which the data will be stored.

        Returns
        -------
        None

        """
        if not os.path.exists(path_local):
            raise Exception("path does not exist {}".format(path_local))
        with open(path_local) as config_file:
            data = json.load(config_file)
        database_reference = self.construct_reference(refernce_name)
        self.upload_data_to_reference(data, database_reference)

    def get_data(self, reference_name):
        """
        Retrieves data from the Firebase Realtime Database under the specified reference name.

        Parameters
        ----------
        reference_name : str
            The name of the reference under which the data is stored.

        Returns
        -------
        data : dict
            The retrieved data in dictionary format.

        """
        database_reference = self.construct_reference(reference_name)
        return self.get_data_from_reference(database_reference)

    def get_data_from_child_reference(self, reference_name, child_name):
        """
        Retreives data from the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        reference_name : str
            The name of the reference under which the child exists.
        child_name : str
            The name of the reference under which the data is stored.

        Returns
        -------
        data : dict
            The retrieved data in dictionary format.

        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        return self.get_data_from_reference(database_reference)

    def get_data_from_deep_reference(self, reference_list):
        """
        Retreives data from the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        data : Any
            The data to be uploaded, needs to be JSON serializable.
        reference_list : list of str
            The names in sequence order in which the is nested.

        Returns
        -------
        data : dict
            The retrieved data in dictionary format.
        """
        database_reference = self.construct_reference_from_list(reference_list)
        return self.get_data_from_reference(database_reference)

    def delete_data(self, reference_name):
        """
        Deletes data from the Firebase Realtime Database under specified reference name.

        Parameters
        ----------
        reference_name : str
            The name of the reference under which the child should exist.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference(reference_name)
        self.delete_data_from_reference(database_reference)

    def delete_data_from_child_reference(self, reference_name, child_name):
        """
        Deletes data from the Firebase Realtime Database under specified reference name & child name.

        Parameters
        ----------
        reference_name : str
            The name of the reference under which the child should exist.
        child_name : str
            The name of the reference under which the data will be stored.

        Returns
        -------
        None

        """
        database_reference = self.construct_child_refrence(reference_name, child_name)
        self.delete_data_from_reference(database_reference)

    def delete_data_from_deep_reference(self, reference_list):
        """
        Deletes data from the Firebase Realtime Database under specified reference names in list order.

        Parameters
        ----------
        reference_list : list of str
            The names in sequence order in which the data should be nested for upload.

        Returns
        -------
        None

        """
        database_reference = self.construct_reference_from_list(reference_list)
        self.delete_data_from_reference(database_reference)
