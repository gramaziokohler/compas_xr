import os
import sys
import json


from compas_xr.realtime_database.realtime_database_interface import RealtimeDatabaseInterface
import clr
import threading
from compas.data import json_dumps,json_loads

try:
    from urllib.request import urlopen    
except ImportError:
    from urllib import urlopen


lib_dir = os.path.join(os.path.dirname(__file__), "dependencies")
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

clr.AddReference("Firebase.Auth.dll")
clr.AddReference("Firebase.dll")
clr.AddReference("LiteDB.dll")
clr.AddReference("System.Reactive.dll")

from Firebase.Auth import FirebaseAuthConfig
from Firebase.Auth import FirebaseAuthClient
from Firebase.Database import FirebaseClient
from Firebase.Database.Query import QueryExtensions

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
    database : FirebaseClient
        The FirebaseClient instance representing the connection to the Firebase Realtime Database.
    _shared_database : FirebaseClient, class attribute
        The shared FirebaseClient instance representing the connection to the Firebase Realtime Database.

    Methods
    -------
    _ensure_database() : FirebaseClient
        Ensures that the database connection is established. If the connection is not yet established, it initializes it. If the connection is already established, it returns the existing connection.

    Raises
    ------
    Exception
        If the configuration file does not exist at the provided path or if the database could not be initialized.

    Examples
    --------
    >>> db = RealtimeDatabase('path/to/config.json')
    >>> db.config_path
    """
    _shared_database = None

    def __init__(self, config_path):
        self.config_path = config_path
        self.database = self._ensure_database()

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
            database_url = config["databaseURL"]
            database_client = FirebaseClient(database_url)
            RealtimeDatabase._shared_database = database_client

        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize Database!")

        return RealtimeDatabase._shared_database

    def _start_async_call(self, fn, timeout=10):
        """
        Manages asynchronous calls to the database.
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

    #TODO: Can this be configured to be a global callback for all methods where I pass the task and the result? This would simplify the code a lot.
    def _task_callback(self, task, result):
        task_awaiter = task.GetAwaiter()
        task_awaiter.OnCompleted(lambda: result["event"].set())
        result["event"].wait()
        result["data"] = True

    def construct_reference(self, parentname):
        """
        Constructs a database reference under the specified parent name.

        Parameters
        ----------
        parentname : str
            The name of the parent under which the reference will be constructed.

        Returns
        -------
        :class: 'Firebase.Database.Query.ChildQuery'
            The constructed database reference.

        """
        database_reference = RealtimeDatabase._shared_database
        reference = database_reference.Child(parentname)
        return reference

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
        :class: 'Firebase.Database.Query.ChildQuery'
            The constructed database reference.

        """
        database_reference = RealtimeDatabase._shared_database
        childquery = database_reference.Child(parentname)
        child_reference = QueryExtensions.Child(childquery, childname)
        return child_reference

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
        :class: 'Firebase.Database.Query.ChildQuery'
            The constructed database reference.

        """
        database_reference = RealtimeDatabase._shared_database
        childquery = database_reference.Child(parentname)
        child_reference = QueryExtensions.Child(childquery, childname)
        grand_child_reference = QueryExtensions.Child(child_reference, grandchildname)
        return grand_child_reference

    def construct_reference_from_list(self, reference_list):
        """
        Constructs a database reference under the specified refrences in list order.

        Parameters
        ----------
        reference_list : list of str
            The name of the parent under which the reference will be constructed.

        Returns
        -------
        :class: 'Firebase.Database.Query.ChildQuery'
            The constructed database reference.

        """
        reference = RealtimeDatabase._shared_database
        for ref in reference_list:
            if ref == reference_list[0]:
                reference = reference.Child(ref)
            else:
                reference = QueryExtensions.Child(reference, ref)
        return reference

    def upload_data_to_reference(self, data, database_reference):
        """
        Method for uploading data to a constructed database reference.

        Parameters
        ----------
        data : Any
            The data to be uploaded. Data should be JSON serializable.
        database_reference: 'Firebase.Database.Query.ChildQuery'
            Reference to the database location where the data will be uploaded.

        Returns
        -------
        None
        """
        self._ensure_database()
        serialized_data = json_dumps(data)
        def _begin_upload(result):
            uploadtask = database_reference.PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        self._start_async_call(_begin_upload)

    def get_data_from_reference(self, database_reference):
        """
        Method for retrieving data from a constructed database reference.

        Parameters
        ----------
        database_reference: 'Firebase.Database.Query.ChildQuery'
            Reference to the database location where the data will be uploaded.

        Returns
        -------
        dict
            The retrieved data as a dictionary.

        """
        self._ensure_database()
        def _begin_build_url(result):
            urlbuldtask = database_reference.BuildUrlAsync()
            task_url = urlbuldtask.GetAwaiter()
            task_url.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = urlbuldtask.Result
        url = self._start_async_call(_begin_build_url)
        json_data = self._get_file_from_remote(url)

        #TODO: json.load(data) vs. json_loads(data)
        """
        This is because error will be thrown with json_loads(data)...
        Because I cannot gaurentee that all data will be filled (FIREBASE DOES NOT UPLOAD NULL VALUES)
        Therefore, unless the data is completely filled json_loads(data) will throw an error.

        """
        data = json.loads(json_data)
        return data

    def delete_data_from_reference(self, database_reference):
        """
        Method for uploading data to a constructed database reference.

        Parameters
        ----------
        data : Any
            The data to be uploaded. Data should be JSON serializable.
        database_reference: 'Firebase.Database.Query.ChildQuery'
            Reference to the database location where the data will be uploaded.

        Returns
        -------
        None
        """
        self._ensure_database()
        def _begin_delete(result):
            deletetask = database_reference.DeleteAsync()
            delete_data = deletetask.GetAwaiter()
            delete_data.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        self._start_async_call(_begin_delete)

    def stream_data_from_reference(self, callback, database_reference):
        raise NotImplementedError("Function Under Developement")