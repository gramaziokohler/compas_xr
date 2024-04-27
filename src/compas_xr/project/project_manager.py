import os

from compas.data import json_dumps
from compas.data import json_loads

from compas_xr.realtime_database import RealtimeDatabase
from compas_xr.storage import Storage


class ProjectManager(object):

    def __init__(self, config_path):

        if not os.path.exists(config_path):
            raise Exception("Could not create Storage or Database with path {}!".format(config_path))
        self.storage = Storage(config_path)
        self.database = RealtimeDatabase(config_path)

    # Functions for uploading Assemblies to the Database and Storage
    def upload_assembly_all_to_database(self, assembly, parentname):

        # Get data from the assembly
        data = assembly.__data__

        # Upload data using Database Class
        self.database.upload_data_all(data, parentname)

    # TODO: Integrated in toggle for removing joint keys.
    def upload_assembly_to_database(self, assembly, parentname, parentparamater, parameters, joints):

        # Get data from the assembly
        data = assembly.__data__

        # Create Data Structure form Assembly
        paramaters_nested = {}

        for param in parameters:
            values = data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)

        if joints == False:

            joint_keys = []
            elements = paramaters_nested[param]

            for item in elements:
                values = elements[item]
                if values["type"] == "joint":
                    joint_keys.append(item)

            for key in joint_keys:
                elements.pop(key)

        # Upload
        self.database.upload_data_all(paramaters_nested, parentname)

    def upload_assembly_aschild_to_database(self, assembly, parentname, childname, parentparameter, childparameter):

        # Get data from the assembly
        data = assembly.__data__

        # Get Assembly Information from Database
        assembly_info = data[parentparameter][childparameter]

        self.database.upload_data_aschild(assembly_info, parentname, childname)

    def upload_assembly_aschildren_to_database(
        self, assembly, parentname, childname, parentparameter, childparameter, parameters
    ):

        # Get data from the assembly
        data = assembly.__data__

        for param in parameters:
            values = data[parentparameter][childparameter][param]
            self.database.upload_data_aschildren(values, parentname, childname, param)

    def upload_assembly_to_storage(self, path_on_cloud, assembly):

        # Turn Assembly to data
        data = json_dumps(assembly, pretty=True)  # TODO: json_dump vs json_dumps? ALSO Pretty can be false.

        # upload data to storage from the storage class method
        self.storage.upload_data(path_on_cloud, data)

    # Function for getting assemblies from Storage
    def get_assembly_from_storage(self, path_on_cloud):

        data = self.storage.get_data(path_on_cloud)

        # TODO: I am not sure why, but when I use the get data, this needs to happen twice for it to return an assembly
        assembly = json_loads(data)

        return assembly
