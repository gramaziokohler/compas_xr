import os
import sys
import json
from compas.data import json_dumps,json_loads
from compas_timber import assembly as TA
from compas_xr.realtime_database.realtime_database_interface import RealtimeDatabaseInterface
import clr
import threading
from compas.datastructures import Assembly
from compas.data import json_dumps,json_loads, json_load
from System.IO import FileStream, FileMode, MemoryStream, Stream
from System.Text import Encoding
from System.Threading import (
    ManualResetEventSlim,
    CancellationTokenSource,
    CancellationToken)
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

from Firebase.Database import FirebaseClient
from Firebase.Database.Query import FirebaseQuery, QueryExtensions
from Firebase.Database import Streaming

# #TODO: GET RID OF DEFAULT CONFIG PATH ALWAYS PASS CONFIG PATH.
# # Get the current file path
# CURRENT_FILE_PATH = os.path.abspath(__file__)
# # print (CURRENT_FILE_PATH)

# # Define the number of levels to navigate up
# LEVELS_TO_GO_UP = 2

# #Construct File path to the correct location
# PARENT_FOLDER = os.path.abspath(os.path.join(CURRENT_FILE_PATH, "../" * LEVELS_TO_GO_UP))

# # Enter another folder
# TARGET_FOLDER = os.path.join(PARENT_FOLDER, "data")
# DEFAULT_CONFIG_PATH = os.path.join(TARGET_FOLDER, "firebase_config.json")

"""
TODO: add proper exceptions. This is a function by function review.
TODO: add proper comments.
"""

class RealtimeDatabase(RealtimeDatabaseInterface):

    # Class attribute for the shared firebase database reference
    _shared_database = None

    # def __init__(self, config_path = None):
        
    #     pass
    
    def __init__(self, config_path = None):
        
        self.config_path = config_path #or DEFAULT_CONFIG_PATH
        self.database = self._ensure_database()

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

    #Internal Class Structure Functions
    def _start_async_call(self, fn, timeout=10):
        print ("inside of start async")
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
            print (get)

        except:
            raise Exception("unable to get file from url {}".format(url))
        
        if get is not None and get != "null":
            return get    
        
        else:
            raise Exception("unable to get file from url {}".format(url))
        
    
    #Functions for building Child References: Happens in 3 types of methods: Upload, Download, and Delete
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


    #Functions for adding attributes to assemblies
    #TODO: NEEDS TO BE MOVED
    def add_assembly_attributes(self, assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None): #DONE
        
        data_type_list = ['0.Cylinder','1.Box','2.ObjFile','3.Mesh']

        data = assembly.data
        graph = assembly.graph.data
        graph_node = graph["node"]

        for key in graph_node:
            graph_node[str(key)]['type_id'] = key
            graph_node[str(key)]['type_data'] = data_type_list[data_type]
            graph_node[str(key)]['is_built'] = False
            graph_node[str(key)]['is_planned'] = False
            graph_node[str(key)]['placed_by'] = "human"

        for k in robot_keys:
            graph_node[str(k)]['placed_by'] = "robot"

        if built_keys:
            for l in built_keys:
                graph_node[str(l)]['is_built'] = True

        if planned_keys:
            for m in planned_keys:
                graph_node[str(m)]['is_planned'] = True

        assembly = Assembly.from_data(data)

        return assembly
    #TODO: NEEDS TO BE MOVED
    def add_assembly_attributes_timbers(self, assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):#DONE
        
        data_type_list = ['0.Cylinder','1.Box','2.ObjFile','3.Mesh']

        data = assembly.data
        beam_keys = assembly.beam_keys
        graph = assembly.graph.data
        graph_node = graph["node"]

        for key in beam_keys:
            graph_node[str(key)]['type_id'] = key
            graph_node[str(key)]['type_data'] = data_type_list[data_type]
            graph_node[str(key)]['is_built'] = False
            graph_node[str(key)]['is_planned'] = False
            graph_node[str(key)]['placed_by'] = "human"

        for k in robot_keys:
            if k in beam_keys:
                graph_node[str(k)]['placed_by'] = "robot"

        if built_keys:
            for l in built_keys:
                    if l in beam_keys:
                        graph_node[str(l)]['is_built'] = True

        if planned_keys:
            for m in planned_keys:
                    if m in beam_keys:
                        graph_node[str(m)]['is_planned'] = True

        timber_assembly = TA.assembly.TimberAssembly.from_data(data)

        return timber_assembly


    #Functions for uploading various types of data
    def upload_file_all(self, path_local, parentname): #DONE

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
        print ("upload complete")

    def upload_file(self, path_local, parentname, parentparamater, parameters): #DONE

        #Ensure Database Connection
        self._ensure_database()

        if os.path.exists(path_local):

            with open(path_local) as json_file:
                json_data = json.load(json_file)
            
        else:
            raise Exception("path does not exist {}".format(path_local))
        
        parameters_list = {}
    
        paramaters_nested = {}
        for param in parameters:
            values = json_data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)

        parameters_list.update(paramaters_nested)

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

    #This function is only for first level paramaters ex. "Attributes" and "Graph" 
    def upload_file_baselevel(self, path_local, parentname, parameters): #DONE

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


    #TODO: NEEDS TO BE MOVED
    def upload_assembly_all(self, assembly, parentname): #DONE

        #Ensure Database Connection
        self._ensure_database()

        data = assembly.data
        serialized_data = json_dumps(data)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            print ("inside of begin upload")
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            print (uploadtask)
            task_upload = uploadtask.GetAwaiter()
            print (task_upload)
            task_upload.OnCompleted(lambda: result["event"].set())
            print
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print (upload)

    #TODO: NEEDS TO BE MOVED
    def upload_assembly(self, assembly, parentname, parentparamater, parameters):#DONE
        
        #Ensure Database Connection
        self._ensure_database()

        data = assembly.data
        
        parameters_list = {}

        paramaters_nested = {}
        
        for param in parameters:
            print (param)
            values = data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)
        parameters_list.update(paramaters_nested)

        serialized_data = json_dumps(parameters_list)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print (upload)

    def upload_data_all(self, data, parentname): #DONE

        #Ensure Database Connection
        self._ensure_database()

        serialized_data = json_dumps(data)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            print (task_upload)
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print ("upload complete")
    
    def upload_data(self, data, parentname, parentparamater, parameters): #DONE
            
        #Ensure Database Connection
        self._ensure_database()

        parameters_list = {}

        #Upload Nested Data or not.
        paramaters_nested = {}
        
        for param in parameters:
            print (param)
            values = data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)
        parameters_list.update(paramaters_nested)

        serialized_data = json_dumps(parameters_list)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print (upload)


    #TODO: CREATE MATCHING METHODS FOR DATA?     
    def upload_file_aschild_all(self, path_local, parentname, childname): #DONE

        #Ensure Database Connection
        self._ensure_database()

        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)

        else:
            raise Exception("path does not exist {}".format(path_local))

        serialized_data = json_dumps(json_data)
                
        def _begin_upload(result):
            new_childreference = self._construct_childreference(parentname,childname)
            uploadtask = new_childreference.PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)

    def upload_file_aschild(self, path_local, parentname, childname, parentparameter, childparameter): #DONE
           
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

    def upload_file_aschildren(self, path_local, parentname, childname, parentparameter, childparameter, parameters): #DONE
            
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

    #TODO: SUBSCRIBE TO PARENT... parentname function Needs to be fixed.
    def stream_parent(self, callback, parentname): #NEEDS TO BE FIXED

        #Ensure Database Connection
        self._ensure_database()

        database_reference = RealtimeDatabase._shared_database

        downloadevent = database_reference.Child(parentname).AsObservable[object]()
        print (downloadevent)

        subscription = downloadevent.Subscribe(callback)

    def download_parent(self, parentname): #DONE
       
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

    def download_child(self, parentname, childname): #DONE
        
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
    def delete_parent(self, parentname): #DONE

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

    def delete_child(self, parentname, childname): #DONE

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

    def delete_children(self, parentname, childname, children): #DONE

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
        