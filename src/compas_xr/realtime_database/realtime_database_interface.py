class RealtimeDatabaseInterface(object):
    
    def download_file(self, path_on_cloud, path_local):
        raise NotImplementedError("Implemented on child classes")
     
    def set_json_data(self, json_f, parentname):
        raise NotImplementedError("Implemented on child classes")
    
    def set_json_data_keys(self, json_f, parentname, keys):
        raise NotImplementedError("Implemented on child classes")

    def set_data(self, parentname, data):
        raise NotImplementedError("Implemented on child classes")

    def set_data_keys(self, parentname, data, keys):
        raise NotImplementedError("Implemented on child classes")

    def set_assembly(self, parentname, assembly):
        raise NotImplementedError("Implemented on child classes")

    def set_assembly_keys(self, parentname, assembly, keys):
        raise NotImplementedError("Implemented on child classes")

    def set_assembly_keys_timbers(self, parentname, assembly, keys):
        raise NotImplementedError("Implemented on child classes")

    def add_assembly_attributes(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        raise NotImplementedError("Implemented on child classes")
        
    def add_assembly_attributes_timbers(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        raise NotImplementedError("Implemented on child classes")

    def remove_parent(self, parentname):
        raise NotImplementedError("Implemented on child classes")

    def remove_child(self, parentname, childname):
        raise NotImplementedError("Implemented on child classes")
    
    def remove_children(self, parentname, children):
        raise NotImplementedError("Implemented on child classes")

    def get_json_data_child(self, parentname, childname):
        raise NotImplementedError("Implemented on child classes")
    
    def get_json_data_parent(self, parentname):
        raise NotImplementedError("Implemented on child classes")


