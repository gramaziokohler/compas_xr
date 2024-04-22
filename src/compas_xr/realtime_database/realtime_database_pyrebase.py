from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
from compas_xr.realtime_database.realtime_database_interface import RealtimeDatabaseInterface
import pyrebase
from compas.data import json_dumps,json_loads

class RealtimeDatabase(RealtimeDatabaseInterface):

    # Class attribute for the shared firebase database reference
    _shared_database = None

    def __init__(self, config_path=None):
        self.config_path = config_path
        self._guid = None
        self._ensure_database()

    def _ensure_database(self):
        # Initialize firebase connection and storage only once
        if not RealtimeDatabase._shared_database:
            path = self.config_path
            
            # Load the firebase configuration file from the JSON file if it exists: Else: Print.
            if os.path.exists(path):
                with open(path) as config_file:
                    config = json.load(config_file)

            #TODO: Authorization for Protected Databases

            firebase = pyrebase.initialize_app(config)
            RealtimeDatabase._shared_database = firebase.database()

        # Still no Database? Fail, we can't do anything
        if not RealtimeDatabase._shared_database:
            raise Exception("Could not initialize database!")

    def _construct_reference(self, project_name):
        return RealtimeDatabase._shared_database.child(project_name)
    
    def _construct_child_refrence(self, parentname, childname):
        return RealtimeDatabase._shared_database.child(parentname).child(childname)
    
    def _construct_grandchild_refrence(self, parentname, childname, grandchildname):
        return RealtimeDatabase._shared_database.child(parentname).child(childname).child(grandchildname)
    
    #Functions for uploading .json files specifically
    def upload_file_all(self, path_local, parentname): 
        
        self._ensure_database()
        
        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)
        
        else:
            raise Exception("path does not exist {}".format(path_local))
        
        RealtimeDatabase._shared_database.child(parentname).set(json_data)
        print ("upload complete")

    def upload_file(self, path_local, parentname, parentparameter, parameters): 
        
        self._ensure_database()
        
        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)
                children = []
                
                for param in parameters:
                    values = json_data[parentparameter][param]
                    children.append(values)

        else:
            raise Exception("path does not exist {}".format(path_local))

        for child, param in zip(children, parameters):
            RealtimeDatabase._shared_database.child(parentname).child(param).set(child)
        print ("upload complete")

    def upload_file_baselevel(self, path_local, parentname, parameters): 
        
        self._ensure_database()
        
        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)
                children = []
                
                for param in parameters:
                    values = json_data[param]
                    children.append(values)

        else:
            raise Exception("path does not exist {}".format(path_local))

        for child, param in zip(children, parameters):
            RealtimeDatabase._shared_database.child(parentname).child(param).set(child)
        print ("file uploaded")

    #Functions for uploading Data
    def upload_data_all(self, data, parentname): 
        
        self._ensure_database() 

        #Serialize data
        serialized_data = json_dumps(data)
        
        RealtimeDatabase._shared_database.child(parentname).set(serialized_data)
        print ("data uploaded")

    def upload_data(self, data, parentname,  parentparamater, parameters): 
        #Check Database Reference            
        self._ensure_database() 
        
        #Serialize data
        serialized_data = json_dumps(data)

        children = []

        for param in parameters:
            values = serialized_data[parentparamater][param]
            children.append(values)

        for child, param in zip(children, parameters):
            RealtimeDatabase._shared_database.child(parentname).child(param).set(child)
        print ("upload complete")

    #Functions for uploading and nesting in the database
    def upload_file_aschild(self, path_local, parentname, childname, parentparameter, childparameter): 
        
        self._ensure_database()
        
        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)

        else:
            raise Exception("path does not exist {}".format(path_local))

        #TODO: Check if Serialization is needed.
        values = json_data[parentparameter][childparameter]
        
        RealtimeDatabase._shared_database.child(parentname).child(childname).set(values)
        print ("upload complete")

    def upload_file_aschildren(self, path_local, parentname, childname, parentparameter, childparameter, parameters):
        
        self._ensure_database()
        
        if os.path.exists(path_local):
            with open(path_local) as json_file:
                json_data = json.load(json_file)

        else:
            raise Exception("path does not exist {}".format(path_local))

        children = []
        
        for param in parameters:
            values = json_data[parentparameter][childparameter][param]
            children.append(values)

        for child, param in zip(children, parameters):
            RealtimeDatabase._shared_database.child(parentname).child(childname).child(param).set(child)
        print ("upload complete")
    
    #TODO: CHANGE NAME
    def upload_data_aschild(self, data, parentname, childname):
           
        #Ensure Database Connection
        self._ensure_database()
        
        serialized_data = json_dumps(data)
        
        RealtimeDatabase._shared_database.child(parentname).child(childname).set(serialized_data)
        print("upload complete")

    #TODO: CHANGE NAME
    def upload_data_aschildren(self, data, parentname, childname, name):
            
        #Ensure Database Connection
        self._ensure_database()

        serialized_data = json_dumps(data)

        RealtimeDatabase._shared_database.child(parentname).child(childname).child(name).set(serialized_data)
        print ("upload complete")

    #Functions for retreiving infomation from the database Streaming and Downloading
    def stream_parent(self, callback, parentname): #TODO: Needs to be fixed
        raise NotImplementedError("Function Under Developement")
    
    def get_parent(self, parentname): 
        self._ensure_database()
        dictionary = {}
        database_reference = RealtimeDatabase._shared_database.child(parentname).get()
        
        if database_reference.each():
            for d in database_reference.each():
                dictionary[d.key()] = d.val()
            print ("got parent")
            return dictionary
        
        else:
            raise Exception("Parent not Found in database")

    def get_child(self, parentname, childname): 
        self._ensure_database()
        
        dictionary = {}
        database_reference = RealtimeDatabase._shared_database.child(parentname).child(childname).get()
        
        if database_reference.each():
            for d in database_reference.each():
                dictionary[d.key()] = d.val()
            print ("got child")
            return dictionary
        
        else:
            raise Exception("Child not Found in database")
    
    #Functions for deleting parents and children
    def delete_parent(self, parentname):
        self._ensure_database()
        RealtimeDatabase._shared_database.child(parentname).remove()
        print ("parent deleted")

    def delete_child(self, parentname, childname):
        self._ensure_database()
        RealtimeDatabase._shared_database.child(parentname).child(childname).remove()
        print ("child deleted")

    def delete_children(self, parentname, childname, children):
        self._ensure_database()

        for child in children:
            RealtimeDatabase._shared_database.child(parentname).child(childname).child(child).remove()
        print ("children deleted")
  
