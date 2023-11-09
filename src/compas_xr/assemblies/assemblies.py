
import os
from compas.data import json_dumps,json_loads
from compas_xr.storage import Storage
from compas_xr.realtime_database import RealtimeDatabase

class AssemblyAssistant(object):

    def __init__(self, config_path):

        if os.path.exists(config_path):
            self.storage = Storage(config_path)
            self.database = RealtimeDatabase(config_path)

        # Still no Database? Fail, we can't do anything
        else:
            raise Exception("Could not create Storage or Database with path {}!".format(config_path))
  
    #Functions for uploading Assemblies to the Database and Storage    
    def upload_assembly_all_to_database(self, assembly, parentname): 

        #Get data from the assembly
        data = assembly.data

        # Upload data using Database Class
        self.database.upload_data_all(data, parentname)

    def upload_assembly_to_database(self, assembly, parentname, parentparamater, parameters):
        
        #Get data from the assembly
        data = assembly.data

        #Create Data Structure form Assembly
        paramaters_nested = {}
        
        for param in parameters:
            values = data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)

        #Upload
        self.database.upload_data_all(paramaters_nested, parentname)

    def upload_assembly_aschild_to_database(self, assembly, parentname, childname, parentparameter, childparameter): 

        #Get data from the assembly
        data = assembly.data

        #Get Assembly Information from Database
        assembly_info = data[parentparameter][childparameter]

        self.database.upload_data_aschild(assembly_info, parentname, childname)

    def upload_assembly_aschildren_to_database(self, assembly, parentname, childname, parentparameter, childparameter, parameters):

        #Get data from the assembly
        data = assembly.data

        for param in parameters:
            values = data[parentparameter][childparameter][param]
            self.database.upload_data_aschildren(values, parentname, childname, param)
        
    def upload_assembly_to_storage(self, path_on_cloud, assembly): 
      
        #Turn Assembly to data
        data = json_dumps(assembly, pretty=True)

        #upload data to storage from the storage class method
        self.storage.upload_data(path_on_cloud, data)

    #Function for getting assemblies from Storage
    def get_assembly_from_storage(self, path_on_cloud):
        
        data = self.storage.get_data(path_on_cloud)
        
        #TODO: I am not sure why, but when I use the get data, this needs to happen twice for it to return an assembly
        assembly = json_loads(data)

        return assembly    

