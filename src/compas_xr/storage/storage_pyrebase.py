import pyrebase
import json
import os
from compas.data import Data, json_dumps, json_loads
from compas.datastructures import Assembly
from compas_xr.storage.storage_interface import StorageInterface
# from compas_xr import SCRIPT

# Get the current file path
CURRENT_FILE_PATH = os.path.abspath(__file__)

# Define the number of levels to navigate up
LEVELS_TO_GO_UP = 4

#Construct File path to the correct location
PARENT_FOLDER = os.path.abspath(os.path.join(CURRENT_FILE_PATH, "../" * LEVELS_TO_GO_UP))

# Enter another folder
TARGET_FOLDER = os.path.join(PARENT_FOLDER, "scripts")
DEFAULT_CONFIG_PATH = os.path.join(TARGET_FOLDER, "firebase_config.json")


class Storage(StorageInterface, Data):

    # Class attribute for the shared firebase storage reference
    _shared_storage = None

    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self._guid = None
        print("Creating instance")
        self._ensure_storage()

    def _ensure_storage(self):
        # Initialize firebase connection and storage only once
        if not Storage._shared_storage:
            path = self.config_path #or self.default_config_path

            # Load the firebase configuration file from the JSON file if file exists.
            if os.path.exists(path):
                print(path)
                with open(path) as config_file:
                    config = json.load(config_file)

            else:
                raise Exception("Path Does Not Exist: {}".format(path))

            firebase = pyrebase.initialize_app(config)
            Storage._shared_storage = firebase.storage()

        # Still no storage? Fail, we can't do anything
        if not Storage._shared_storage:
            raise Exception("Could not initialize storage!")

    def upload_file(self, path_on_cloud, path_local):
        self._ensure_storage()
        Storage._shared_storage.child(path_on_cloud).put(path_local)

    def download_file(self, path_on_cloud, path_local):
        self._ensure_storage()
        filename = path_local
        Storage._shared_storage.child(path_on_cloud).download(path_local, filename)

    #TODO: test these functions    
    def add_assembly_attributes(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        
        data_type_list = ['Cylinder','Box','ObjFile','Mesh']
        
        data = assembly.data
        
        data = [data]
        data_nodes = data[0]['graph']['node']
        length = len(data_nodes)
        beam_keys = []
        
        for key in data_nodes:
            data_nodes[key]['type_id'] = key
            data_nodes[key]['type_data'] = data_type_list[data_type]
            data_nodes[key]['is_built'] = False
            data_nodes[key]['is_planned'] = False
            data_nodes[key]['placed_by'] = "human"
            beam_keys.append(key)
        
        for k in robot_keys:
            data_nodes[str(k)]['placed_by'] = "robot"
            
        if built_keys:
            for l in built_keys:
                    data_nodes[str(l)]['is_built'] = True
        
        if planned_keys:
            for m in planned_keys:
                    data_nodes[str(m)]['is_planned'] = True
        
    def add_assembly_attributes_timbers(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):

        data_type_list = ['Cylinder','Box','ObjFile','Mesh']
        
        data = assembly.data
        
        data = [data]
        data_nodes = data[0]['graph']['node']
        length = len(data_nodes)
        joints = {}
        joint_keys = []
        beam_keys = []
        
        for item in joint_keys:
            data_nodes.pop(item)
        
        for key in data_nodes:
            data_nodes[key]['type_id'] = key
            data_nodes[key]['type_data'] = data_type_list[data_type]
            data_nodes[key]['is_built'] = False
            data_nodes[key]['is_planned'] = False
            data_nodes[key]['placed_by'] = "human"
            beam_keys.append(key)
        
        for k in robot_keys:
            data_nodes[str(k)]['placed_by'] = "robot"
            
        if built_keys:
            for l in built_keys:
                    data_nodes[str(l)]['is_built'] = True
        
        if planned_keys:
            for m in planned_keys:
                    data_nodes[str(m)]['is_planned'] = True
        
        data[0]['graph']['joints'] = joints

    def upload_data(self, path_on_cloud, data):
        #Check Storage Refrence
        self._ensure_storage()

        #Serialize data
        serialized_data = json_dumps(data)
        Storage._shared_storage.child(path_on_cloud).put(serialized_data)

    def download_data(self, path_on_cloud, path_local):
        #Check Storage Reference
        self._ensure_storage()
        
        #Download File to location
        filename = path_local
        Storage._shared_storage.child(path_on_cloud).download(path_local, filename)
        
        # Load the JSON Data File and desearlize it.
        #TODO: Check if you need + filename?
        if os.path.exists(path_local):
            with open(path_local) as data:
                data = json.load(data)
        else:
            raise Exception("Path Does Not Exist: {}".format(path_local))
                
        #Deserialize data
        desearlize_data = json_loads(data)
        
        return desearlize_data

    def upload_assembly(self, path_on_cloud, assembly):
        #Check Storage Refrence
        self._ensure_storage()

        #Turn assembly to data
        data = assembly.data

        #Serialize data
        serialized_data = json_dumps(data)
        Storage._shared_storage.child(path_on_cloud).put(serialized_data)

    def download_assembly(self, path_on_cloud, path_local, assembly):
        #Check Storage Reference
        self._ensure_storage()
        
        #Download File to location
        filename = path_local
        Storage._shared_storage.child(path_on_cloud).download(path_local, filename)
        
        # Load the JSON Data File and desearlize it.
        #TODO: Check if you need + filename?
        if os.path.exists(path_local):
            with open(path_local) as data:
                data = json.load(data)
        else:
            raise Exception("Path Does Not Exist: {}".format(path_local))
                
        #Deserialize data
        desearlize_data = json_loads(data)
        
        #Create an assembly from data
        assembly = Assembly.from_data(desearlize_data)

        return assembly

    @property
    def data(self):
        return dict(config_path=self.config_path)

    @data.setter
    def data(self, value):
        self.config_path = value["config_path"]

    @classmethod
    def from_data(cls, data):
        config_path = data["config_path"]
        return cls(config_path)
