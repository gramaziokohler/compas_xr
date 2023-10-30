import os
import sys
import json
from compas.data import json_dumps,json_loads
from compas_timber import assembly as TA
from compas_xr.realtime_database.realtime_database_interface import RealtimeDatabaseInterface
import clr
import threading
from compas.datastructures import Assembly
from compas.data import json_dumps,json_loads
from System.IO import FileStream, FileMode, MemoryStream, Stream
from System.Text import Encoding
from System.Threading import (
    ManualResetEventSlim,
    CancellationTokenSource,
    CancellationToken)
try:
    # from urllib.request import urlopen
    from urllib.request import urlretrieve
except ImportError:
    # from urllib2 import urlopen
    from urllib import urlretrieve


lib_dir = os.path.join(os.path.dirname(__file__), "dependencies")
print (lib_dir)
if lib_dir not in sys.path:
    sys.path.append(lib_dir)


clr.AddReference("Firebase.Auth.dll")
clr.AddReference("Firebase.dll")
clr.AddReference("Firebase.Storage.dll")

from Firebase.Database import FirebaseClient
from Firebase.Database.Query import FirebaseQuery
# from Firebase.Auth import FirebaseAuthConfig
# # from Firebase.Auth import FirebaseConfig
# from Firebase.Auth import FirebaseAuthClient
# from Firebase.Auth.Providers import FirebaseAuthProvider
# from Firebase.Storage import FirebaseStorage

# Get the current file path
CURRENT_FILE_PATH = os.path.abspath(__file__)
# print (CURRENT_FILE_PATH)

# Define the number of levels to navigate up
LEVELS_TO_GO_UP = 2

#Construct File path to the correct location
PARENT_FOLDER = os.path.abspath(os.path.join(CURRENT_FILE_PATH, "../" * LEVELS_TO_GO_UP))

# Enter another folder
TARGET_FOLDER = os.path.join(PARENT_FOLDER, "data")
DEFAULT_CONFIG_PATH = os.path.join(TARGET_FOLDER, "firebase_config.json")

class RealtimeDatabase(RealtimeDatabaseInterface):

    # Class attribute for the shared firebase database reference
    _shared_database = None
    
    # def __init__(self, config_path = None):
        
    #     pass
    
    def __init__(self, config_path = None):
        
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        # self.auth_client = None
        # self.storage_client = None
        self.database = self._ensure_database()

    def _ensure_database(self):

        # Initialize Firebase connection and databse only once
        if not RealtimeDatabase._shared_database:
            path = self.config_path
            print ("This is your path" + path)

            # Load the Firebase configuration file from the JSON file if the file exists
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)

                # Initialize Firebase authentication and storage
                # api_key = config["apiKey"]
                # auth_config_test = FirebaseAuthConfig()
                # auth_config = FirebaseAuthProvider(FirebaseConfig(api_key))
                # auth_config.api_key = config["apiKey"]  # Set the API key separately
                # auth_client = FirebaseAuthClient(config_file)

                #Initilize Storage instance from storageBucket
                database_client = FirebaseClient(config["databaseURL"])
                print (database_client)
                RealtimeDatabase._shared_database = database_client

        else:
            raise Exception("Path Does Not Exist: {}".format(path))

        # Still no storage? Fail, we can't do anything
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
    
    #Functions for adding attributes to assemblies
    def add_assembly_attributes(self, assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        
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

    def add_assembly_attributes_timbers(self, assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        
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
    #TODO: Function for adding children to an existing parent
    def upload_file_all(self, json_path, parentname):
        
        if RealtimeDatabase._shared_database:

            with open(json_path) as json_file:
                json_data = json.load(json_file)
            
            serialized_data = json_dumps(json_data)
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

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")

    def upload_file(self, json_path, parentname, parentparamater, parameters):
        
        if RealtimeDatabase._shared_database:

            with open(json_path) as json_file:
                json_data = json.load(json_file)
            
            parameters_list = {}
        
            paramaters_nested = {}
            for param in parameters:
                print (param)
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
            print (upload)

        else:
            raise Exception("You need a DB reference!")

    def upload_assembly_all(self, assembly, parentname):
        
        if RealtimeDatabase._shared_database:

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

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")
    
    def upload_assembly(self, assembly, parentname, parentparamater, parameters):
        
        if RealtimeDatabase._shared_database:

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

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")

    def upload_data_all(self, data, parentname):
        
        if RealtimeDatabase._shared_database:

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

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")
    
    def upload_data(self, data, parentname, parentparamater, parameters, nestedparams=True):
        
        if RealtimeDatabase._shared_database:
            
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

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")

    #TODO: Functions for reading from RealTimeDB


    #This function is only for first level paramaters, or would be great if we want to hard code "Graph param"    
    def upload_file_baselevel(self, json_path, parentname, parameters):
        
        if RealtimeDatabase._shared_database:

            with open(json_path) as json_file:
                json_data = json.load(json_file)
            
            parameters_list = {}

            for param in parameters:
                values = json_data[param]
                parameters_dict = {param: values}
                parameters_list.update(parameters_dict)
            
            serialized_data = json_dumps(parameters_list)
            database_reference = RealtimeDatabase._shared_database 

            def _begin_upload(result):
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

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")

    #TODO: This did not work, but reference code looks like we can double nest child references. This needs to be checked.
    def upload_file_all_as_child(self, json_path, parentname, childname):
        
        if RealtimeDatabase._shared_database:

            with open(json_path) as json_file:
                json_data = json.load(json_file)
            
            serialized_data = json_dumps(json_data)
            database_reference = RealtimeDatabase._shared_database
            # print (type(database_reference))
            # parent_reference = database_reference.Child(parentname)
            # print (type(parent_reference))
            # parent_query = FirebaseQuery(parent_reference, database_reference)
            # print (parent_reference)

            def _begin_upload(result):
                print ("inside of begin upload")
                uploadtask = database_reference.Child(parentname).PostAsync(serialized_data)
                # print (random) 
                # uploadtask = database_reference.Child(parentname).Child(childname).PutAsync(serialized_data)
                print (uploadtask)
                task_upload = uploadtask.GetAwaiter()
                print (task_upload)
                task_upload.OnCompleted(lambda: result["event"].set())
                print
                result["event"].wait()
                result["data"] = True
            
            upload = self._start_async_call(_begin_upload)
            print (upload)

        #TODO: Do I need this?
        else:
            raise Exception("You need a DB reference!")
