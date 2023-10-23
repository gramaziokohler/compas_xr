class StorageInterface(object):
    def download_file(self, path_on_cloud, path_local):
        raise NotImplementedError("Implemented on child classes")

    def upload_file(self, path_on_cloud, path_local):
        raise NotImplementedError("Implemented on child classes")

    #TODO: Should these functions stay?
    def add_assembly_attributes(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        raise NotImplementedError("Implemented on child classes")

    def add_assembly_attributes_timbers(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        raise NotImplementedError("Implemented on child classes")

    def upload_data(self, path_on_cloud, data):
        raise NotImplementedError("Implemented on child classes")

    def download_data(self, path_on_cloud, path_local):
        raise NotImplementedError("Implemented on child classes")

    def upload_assembly(self, path_on_cloud, assembly):
        raise NotImplementedError("Implemented on child classes")

    def download_assembly(self, path_on_cloud, path_local, assembly):
        raise NotImplementedError("Implemented on child classes")
