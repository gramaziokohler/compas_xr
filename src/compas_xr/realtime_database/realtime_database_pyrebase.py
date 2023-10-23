from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from compas_xr import SCRIPT

import os
import json
import pyrebase
from compas.data import json_dumps,json_loads

# Get the current file path
CURRENT_FILE_PATH = os.path.abspath(__file__)

# Define the number of levels to navigate up
LEVELS_TO_GO_UP = 4

#Construct File path to the correct location
PARENT_FOLDER = os.path.abspath(os.path.join(CURRENT_FILE_PATH, "../" * LEVELS_TO_GO_UP))

# Enter another folder
TARGET_FOLDER = os.path.join(PARENT_FOLDER, "scripts")
DEFAULT_CONFIG_PATH = os.path.join(TARGET_FOLDER, "firebase_config.json")

class RealtimeDatabase(object):

    # Class attribute for the shared firebase database reference
    _shared_database = None

    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self._guid = None
        print("Creating instance")
        self._ensure_database()

    def _ensure_database(self):
        # Initialize firebase connection and storage only once
        if not RealtimeDatabase._shared_database:
            path = self.config_path or DEFAULT_CONFIG_PATH
            # Load the firebase configuration file from the JSON file if it exists: Else: Print.
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)

            firebase = pyrebase.initialize_app(config)
            RealtimeDatabase._shared_database = firebase.database()

        # Still no Database? Fail, we can't do anything
        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize database!")

    def dummy(self):
        self._ensure_database()
        message = "you are accessing database via proxy"
        return message

    #TODO: TEST: This function sets the entirity of the json to database
    def set_json_data(self, json_f, parentname):
        
        self._ensure_database()
        with open(json_f) as json_file:
            json_data = json.load(json_file)
        
        RealtimeDatabase._shared_database.child(parentname).set(json_data)

    #TODO: TEST: This fuction sets only specific keys from the json to database
    def set_json_data_keys(self, json_f, parentname, keys):
        
        self._ensure_database()
        with open(json_f) as json_file:
            json_data = json.load(json_file)
            children = []
            for key in keys:
                values = json_data[key]
                children.append(values)

        for child, key in zip(children, keys):
            RealtimeDatabase._shared_database.child(parentname).child(key).set(child)

    #TODO: TEST: Upload data compas
    def set_data(self, parentname, data):
        self._ensure_database() 

        #Serialize data
        serialized_data = json_dumps(data)
        
        RealtimeDatabase._shared_database.child(parentname).set(serialized_data)

    #TODO: TEST: Upload keys compas data
    def set_data_keys(self, parentname, data, keys):
        #Check Database Reference            
        self._ensure_database() 
        
        #Serialize data
        serialized_data = json_dumps(data)

        children = []

        for key in keys:
            values = serialized_data[key]
            children.append(values)

        for child, key in zip(children, keys):
            RealtimeDatabase._shared_database.child(parentname).child(key).set(child)

    #TODO: TEST: Set Assembly
    def set_assembly(self, parentname, assembly):
        #Check Database Refrence
        self._ensure_database() 

        #Turn assembly to data
        data = assembly.data

        #Serialize data
        serialized_data = json_dumps(data)
        RealtimeDatabase._shared_database.child(parentname).set(serialized_data)

    #TODO: TEST: Set Assembly keys
    def set_assembly_keys(self, parentname, assembly, keys):
        
        #Check Database Refrence
        self._ensure_database() 

        #Turn assembly to data
        data = assembly.data

        #Serialize data
        serialized_data = json_dumps(data)

        children = []
        for key in keys:
            values = serialized_data[key]
            children.append(values)

        #Set Child and key to database
        for child, key in zip(children, keys):
            RealtimeDatabase._shared_database.child(parentname).child(key).set(child)

    #TODO: TEST: Set Timbers Assembly keys
    def set_assembly_keys_timbers(self, parentname, assembly, keys):
        
        #Check Database Refrence
        self._ensure_database() 

        #Turn assembly to data
        data = assembly.data

        #Serialize data
        serialized_data = json_dumps(data)

        children = []
        for key in keys:
            values = serialized_data["graph"][key]
            children.append(values)

        #Set Child and key to database
        for child, key in zip(children, keys):
            RealtimeDatabase._shared_database.child(parentname).child(key).set(child)

    #TODO: TEST ADD ATTRIBUTES TO ASSEMBLY
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

    #TODO: Remove a parent: CHECK WHAT HAPPENS IF YOU TRY TO REMOVE A PARENT THAT DOES NOT EXIST
    def remove_parent(self, parentname):
        self._ensure_database()
        RealtimeDatabase._shared_database.child(parentname).remove()

    #TODO: Remove Child: CHECK WHAT HAPPENS IF YOU TRY TO REMOVE A CHILD THAT DOES NOT EXIST
    def remove_child(self, parentname, childname):
        self._ensure_database()
        RealtimeDatabase._shared_database.child(parentname).child(childname).remove()
    
    #TODO: Remove children: CHECK WHAT HAPPENS IF YOU TRY TO REMOVE A CHILD THAT DOES NOT EXIST
    def remove_children(self, parentname, children):
        self._ensure_database()

        for child in children:
            RealtimeDatabase._shared_database.child(parentname).child(child).remove()

    def get_json_data_child(self, parentname, childname):
        self._ensure_database()
        json_data = {}
        data = RealtimeDatabase._shared_database.child(parentname).child(childname).get()
        if data.each():
            for d in data.each():
                json_data[d.key()] = d.val()
            return json_data
        else:
            raise Exception("Child not Found in database")
            # dt = RealtimeDatabase._shared_database.child(parentname).child(childname).get().val()
            # return dt
    
    def get_json_data_parent(self, parentname):
        self._ensure_database()
        json_data = {}
        data = RealtimeDatabase._shared_database.child(parentname).get()
        if data.each():
            for d in data.each():
                json_data[d.key()] = d.val()
            return json_data
        else:
            raise Exception("Parent not Found in database")
            # dt = RealtimeDatabase._shared_database.child(parent_name).get().val()
            # return dt



  
    # Old functions Not sure if Useful: will check with testing
    def stream_handler(self,message):
        self._ensure_database()
        print(message["event"])
        print(message["path"])
        print(message["data"])
    
    def get_keys_built(self):

        self._ensure_database()
        keys_built = []
        keys = RealtimeDatabase._shared_database.child("Built Keys").get()
        if keys.each():
            for key in keys.each():
                # print("key to built key ", key.key())
                keys_built.append(key.val())
        return keys_built
   
    # Dont believe we actually need this either
    def set_keys_built(self, keys):
        self._ensure_database()
        data = {}
        for key in keys:
            data[str(key)] = str(key)
        RealtimeDatabase._shared_database.child("Built Keys").set(data)

    #Don't actually need
    def remove_key_built(self, key):
        self._ensure_database()
        RealtimeDatabase._shared_database.child("Built Keys").child(str(key)).remove()

    #Dont actually need
    def add_key_built(self, new_key_built):
        self._ensure_database()
        RealtimeDatabase._shared_database.child("Built Keys").update({str(new_key_built): str(new_key_built)})

    # get users' ids: REVIEW THESE
    def get_users(self):
        self._ensure_database()
        users_ids = []
        users = RealtimeDatabase._shared_database.child("Users").get()
        for user in users.each():
            print(user.key())
            users_ids.append(user.key())
            # print("Selected Key is ", user.val()["selectedKey"])
            # print("Selected by user Nr.", user.val()["userID"])
        return users_ids

    #Not sure if needed: user as input?
    def get_users_attribute(self, attribute):

        self._ensure_database()
        users_attributes = []
        users = RealtimeDatabase._shared_database.child("user").get()
        for user in users.each():
            users_attributes.append(user.val()[attribute])
        return users_attributes
    
    #old version of set data for reference, worked with set frame.to_data()
    def set_data_old(self, parentname, data):
        self._ensure_database() 
        RealtimeDatabase._shared_database.child(parentname).set(data)
