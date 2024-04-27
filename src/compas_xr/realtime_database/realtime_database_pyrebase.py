from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os

import pyrebase
from compas.data import json_dumps
from compas.data import json_loads

from compas_xr.realtime_database.realtime_database_interface import RealtimeDatabaseInterface


class RealtimeDatabase(RealtimeDatabaseInterface):
    """
    A RealtimeDatabase is defined by a Firebase configuration path and a shared database reference.

    The RealtimeDatabase class is responsible for initializing and managing the connection to a Firebase Realtime Database.
    It ensures that the database connection is established only once and shared across all instances of the class.

    Parameters
    ----------
    config_path : str
        The path to the Firebase configuration JSON file.

    Attributes
    ----------
    config_path : str
        The path to the Firebase configuration JSON file.
    database : Database
        The Database instance representing the connection to the Firebase Realtime Database.
    _shared_database : Database, class attribute
        The shared Database instance representing the connection to the Firebase Realtime Database.

    Methods
    -------
    _ensure_database() : Database
        Ensures that the database connection is established. If the connection is not yet established, it initializes it. If the connection is already established, it returns the existing connection.

    Raises
    ------
    Exception
        If the configuration file does not exist at the provided path or if the database could not be initialized.

    Examples
    --------
    >>> db = RealtimeDatabase('path/to/config.json')
    """
    _shared_database = None

    def __init__(self, config_path):
        self.config_path = config_path
        self._ensure_database()

    def _ensure_database(self):
        """
        Ensures that the database connection is established.
        If the connection is not yet established, it initializes it.
        If the connection is already established, it returns the existing connection.
        """
        if not RealtimeDatabase._shared_database:
            path = self.config_path
            
            if not os.path.exists(path):
                raise Exception("Could not find config file at path {}!".format(path))
            with open(path) as config_file:
                config = json.load(config_file)
            #TODO: Database Authorization (Works only with public databases)
            firebase = pyrebase.initialize_app(config)
            RealtimeDatabase._shared_database = firebase.database()

        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize database!")

    def construct_reference(self, parentname):
        """
        Constructs a database reference under the specified parent name.

        Parameters
        ----------
        parentname : str
            The name of the parent under which the reference will be constructed.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Database'
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname)
    
    def construct_child_refrence(self, parentname, childname):
        """
        Constructs a database reference under the specified parent name & child name.

        Parameters
        ----------
        parentname : str
            The name of the parent under which the reference will be constructed.
        childname : str
            The name of the child under which the reference will be constructed.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Database'
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname).child(childname)
    
    def construct_grandchild_refrence(self, parentname, childname, grandchildname):
        """
        Constructs a database reference under the specified parent name, child name, & grandchild name.

        Parameters
        ----------
        parentname : str
            The name of the parent under which the reference will be constructed.
        childname : str
            The name of the child under which the reference will be constructed.
        grandchildname : str
            The name of the grandchild under which the reference will be constructed.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Database'
            The constructed database reference.

        """
        return RealtimeDatabase._shared_database.child(parentname).child(childname).child(grandchildname)

    def construct_reference_from_list(self, reference_list):
        """
        Constructs a database reference under the specified refrences in list order.

        Parameters
        ----------
        reference_list : list of str
            The name of the parent under which the reference will be constructed.

        Returns
        -------
        :class: 'pyrebase.pyrebase.Database'
            The constructed database reference.

        """
        reference = RealtimeDatabase._shared_database
        for ref in reference_list:
            reference = reference.child(ref)
        return reference

    def delete_data_from_reference(self, database_reference):
        """
        Method for deleting data from a constructed database reference.

        Parameters
        ----------
        database_reference: 'pyrebase.pyrebase.Database'
            Reference to the database location where the data will be deleted from.

        Returns
        -------
        None
        """
        self._ensure_database()
        database_reference.remove()

    def get_data_from_reference(self, database_reference): 
        """
        Method for retrieving data from a constructed database reference.

        Parameters
        ----------
        database_reference: 'pyrebase.pyrebase.Database'
            Reference to the database location where the data will be retreived from.

        Returns
        -------
        dict
            The retrieved data as a dictionary.

        """
        self._ensure_database()
        database_directory = database_reference.get()
        data = database_directory.val()
        data_dict = dict(data)
        return data_dict

    def stream_data_from_reference(self, callback, database_reference):
        raise NotImplementedError("Function Under Developement")

    def upload_data_to_reference(self, data, database_reference): 
        """
        Method for uploading data to a constructed database reference.

        Parameters
        ----------
        data : Any
            The data to be uploaded. Data should be JSON serializable.
        database_reference: 'pyrebase.pyrebase.Database'
            Reference to the database location where the data will be uploaded.

        Returns
        -------
        None
        """
        self._ensure_database()
        #TODO: Check if it is possible to do this with some sort of serialization for consistency across both?
        # serialized_data = json_dumps(data)
        database_reference.set(data)  
