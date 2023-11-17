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
clr.AddReference("Firebase.Storage.dll")
clr.AddReference("LiteDB.dll")
clr.AddReference("System.Reactive.dll")

from Firebase.Auth import FirebaseAuthConfig
from Firebase.Auth import FirebaseAuthClient
from Firebase.Database import FirebaseClient
from Firebase.Database.Query import QueryExtensions

"""
TODO: add proper comments.
TODO: Review Function todo's
TODO: Authorization for the Database
"""

class RealtimeDatabase(RealtimeDatabaseInterface):

    # Class attribute for the shared firebase database reference
    _shared_database = None
    
    def __init__(self, config_path = None):
        
        self.config_path = config_path #or DEFAULT_CONFIG_PATH
        self.database = self._ensure_database()

    #Internal Class Structure Functions
    def _ensure_database(self):

        # Initialize Firebase connection and databse only once
        if not RealtimeDatabase._shared_database:
            path = self.config_path

            # Load the Firebase configuration file from the JSON file if the file exists
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)

                #TODO: Authorization for database security (Works for now for us because our DB is public)

                #Initilize database instance from the database URL
                database_url = config["databaseURL"]
                database_client = FirebaseClient(database_url)
                RealtimeDatabase._shared_database = database_client
                print ("Shared Database Client Set")
        
        # Still no Database? Fail, we can't do anything
        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize Database!")

        return RealtimeDatabase._shared_database

    def _start_async_call(self, fn, timeout=10):
        
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
        
    def _construct_childreference(self, parentname, childname):
      
        database_reference = RealtimeDatabase._shared_database
        childquery = database_reference.Child(parentname)
        child_reference = QueryExtensions.Child(childquery, childname)

        return child_reference

    def _construct_childrenreference(self, parentname, childname, name):
        
        database_reference = RealtimeDatabase._shared_database
        childquery = database_reference.Child(parentname)
        child_reference = QueryExtensions.Child(childquery, childname)

        childrenreference = QueryExtensions.Child(child_reference, name)

        return childrenreference

    #Functions for uploading .json files specifically
    def upload_file_all(self, path_local, parentname): #Keep: but should be called

        #Ensure Database Connection
        self._ensure_database()

        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)
        
        else:
            raise Exception("path does not exist {}".format(path_local))

        serialized_data = json_dumps(json_data)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)

    def upload_file(self, path_local, parentname, parentparameter, parameters): #Maybe: (move) upload_file_graph_paramaters(file_path, paramaters[edge, dna, node]) (If we keep it)

        #Ensure Database Connection
        self._ensure_database()

        if os.path.exists(path_local):

            with open(path_local) as json_file:
                json_data = json.load(json_file)
            
        else:
            raise Exception("path does not exist {}".format(path_local))
        
        
        paramaters_nested = {}

        for param in parameters:
            values = json_data[parentparameter][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)

        serialized_data = json_dumps(paramaters_nested)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print ("upload complete")

    #This function is only for first level paramaters ex. "Attributes" and "Graph" 
    def upload_file_baselevel(self, path_local, parentname, parameters): #DON'T NEED

        #Ensure Database Connection
        self._ensure_database()

        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)
            
        else:
            raise Exception("path does not exist {}".format(path_local))
        
        parameters_list = {}

        for param in parameters:
            values = json_data[param]
            parameters_dict = {param: values}
            parameters_list.update(parameters_dict)
        
        serialized_data = json_dumps(parameters_list)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print ("upload complete")

    #Functions for uploading Data
    def upload_data_all(self, data, parentname): #Keep: Should be called upload data

        #Ensure Database Connection
        self._ensure_database()

        serialized_data = json_dumps(data)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print ("upload complete")
    
    def upload_data(self, data, parentname, parentparamater, parameters): #DON'T NEED
            
        #Ensure Database Connection
        self._ensure_database()

        #Upload Nested Data or not.
        paramaters_nested = {}
        
        for param in parameters:
            values = data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)
       
        serialized_data = json_dumps(paramaters_nested)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print ("upload complete")

    #Functions for uploading and nesting in the database   
    def upload_file_aschild(self, path_local, parentname, childname, parentparameter, childparameter): #Don't Need - Instead will be upload_file_graph_paramaters() 
           
        #Ensure Database Connection
        self._ensure_database()
 
        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)

        else:
            raise Exception("path does not exist {}".format(path_local))
        
        values = json_data[parentparameter][childparameter]
        serialized_data = json_dumps(values)

        def _begin_upload(result):
            new_childreference = self._construct_childreference(parentname, childname)
            uploadtask = new_childreference.PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)

    def upload_file_aschildren(self, path_local, parentname, childname, parentparameter, childparameter, parameters): # Maybe - (move) Uploading specific Nodes from a file but I dont think you need this functionality would use data 
            
        #Ensure Database Connection
        self._ensure_database()

        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)

        else:
            raise Exception("path does not exist {}".format(path_local))

        for param in parameters:
            
            values = json_data[parentparameter][childparameter][param]
            serialized_data = json_dumps(values)

            def _begin_upload(result):
                new_childreference = self._construct_childrenreference(parentname,childname,param)
                uploadtask = new_childreference.PutAsync(serialized_data)
                task_upload = uploadtask.GetAwaiter()
                task_upload.OnCompleted(lambda: result["event"].set())
                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
    #TODO: CHANGE NAME
    def upload_data_aschild(self, data, parentname, childname): #Keep: Name = upload_data_to_child_directory()
           
        #Ensure Database Connection
        self._ensure_database()
        
        serialized_data = json_dumps(data)

        def _begin_upload(result):
            new_childreference = self._construct_childreference(parentname, childname)
            uploadtask = new_childreference.PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
    #TODO: CHANGE NAME
    def upload_data_aschildren(self, data, parentname, childname, name): #Keep: upload_data_as_single_entry(data, directoryname, childdirectoryname, entryname)
            
        #Ensure Database Connection
        self._ensure_database()

        serialized_data = json_dumps(data)

        def _begin_upload(result):
            new_childreference = self._construct_childrenreference(parentname,childname,name)
            uploadtask = new_childreference.PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)

    #Functions for retreiving infomation from the database Streaming and Downloading
    def stream_parent(self, callback, parentname): #TODO: NEEDS TO BE FIXED #Keep
        raise NotImplementedError("Function Under Developement")
    
        #Ensure Database Connection
        self._ensure_database()

        database_reference = RealtimeDatabase._shared_database

        downloadevent = database_reference.Child(parentname).AsObservable[object]()
        print (downloadevent)

        subscription = downloadevent.Subscribe(callback)

    def get_parent(self, parentname): #Keep: #TODO: It does not return keys of dictionary, just values get_data_main_directory(self, directoryname):
       
        #Ensure Database Connection
        self._ensure_database()
 
        database_reference = RealtimeDatabase._shared_database

        def _begin_build_url(result):
            urlbuldtask = database_reference.Child(parentname).BuildUrlAsync()
            task_url = urlbuldtask.GetAwaiter()
            task_url.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = urlbuldtask.Result
        
        url = self._start_async_call(_begin_build_url)

        data = self._get_file_from_remote(url)
        #TODO: CHECK json.load vs json_loads with Danela or Gonzalo
        dictionary = json.loads(data)
  
        return dictionary

    def get_child(self, parentname, childname): #Keep: get_data_child_directory(self, directoryname, childdirectoryname)
        
        #Ensure Database Connection
        self._ensure_database()

        def _begin_build_url(result):
            database_reference = self._construct_childreference(parentname, childname)
            urlbuldtask = database_reference.BuildUrlAsync()
            task_url = urlbuldtask.GetAwaiter()
            task_url.OnCompleted(lambda: result["event"].set())

            result["event"].wait()
            result["data"] = urlbuldtask.Result
        
        url = self._start_async_call(_begin_build_url)

        data = self._get_file_from_remote(url)
        dictionary = json.loads(data)

        return dictionary

    #Functions for deleting parents and children
    def delete_parent(self, parentname): #Keep: delete_data_main_directory(self, directoryname)

        #Ensure Database Connection
        self._ensure_database()

        database_reference = RealtimeDatabase._shared_database 

        def _begin_delete(result):
            deletetask = database_reference.Child(parentname).DeleteAsync()
            delete_data = deletetask.GetAwaiter()
            delete_data.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        delete = self._start_async_call(_begin_delete)
        print("parent deleted")

    def delete_child(self, parentname, childname): #Keep: delete_data_child_directory(self, directoryname, childdirectoryname)

        #Ensure Database Connection
        self._ensure_database()

        def _begin_delete(result):
            delete_reference = self._construct_childreference( parentname, childname)
            deletetask = delete_reference.DeleteAsync()
            delete_data = deletetask.GetAwaiter()
            delete_data.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        delete = self._start_async_call(_begin_delete)
        print("child deleted")

    def delete_children(self, parentname, childname, children): #Keep: #Keep: delete_data_entries(self, directoryname, childdirectoryname, entries)

        #Ensure Database Connection
        self._ensure_database()

        for child in children:
            def _begin_delete(result):
                
                delete_child_reference = self._construct_childrenreference(parentname, childname, child)
                deletetask = delete_child_reference.DeleteAsync()
                delete_data = deletetask.GetAwaiter()
                delete_data.OnCompleted(lambda: result["event"].set())
                result["event"].wait()
                result["data"] = True
            
            delete = self._start_async_call(_begin_delete)
        print("children deleted")
        