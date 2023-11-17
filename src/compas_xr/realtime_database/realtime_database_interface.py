class RealtimeDatabaseInterface(object):
    
    def upload_file_all(self, path_local, parentname):
        raise NotImplementedError("Implemented on child classes")

    def upload_file(self, path_local, parentname, parentparameter, parameters): 
        raise NotImplementedError("Implemented on child classes")

    def upload_file_baselevel(self, path_local, parentname, parameters): 
        raise NotImplementedError("Implemented on child classes")

    def upload_data_all(self, data, parentname): 
        raise NotImplementedError("Implemented on child classes")
    
    def upload_file_aschild(self, path_local, parentname, childname, parentparameter, childparameter):
        raise NotImplementedError("Implemented on child classes")

    def upload_file_aschildren(self, path_local, parentname, childname, parentparameter, childparameter, parameters):
        raise NotImplementedError("Implemented on child classes")

    def upload_data_aschild(self, data, parentname, childname, parentparameter, childparameter):
        raise NotImplementedError("Implemented on child classes")

    def upload_data_aschildren(self, data, parentname, childname, parentparameter, childparameter, parameters):
        raise NotImplementedError("Implemented on child classes")
    
    def stream_parent(self, callback, parentname):
        raise NotImplementedError("Implemented on child classes")

    def download_parent(self, parentname): 
        raise NotImplementedError("Implemented on child classes")

    def download_child(self, parentname, childname): 
        raise NotImplementedError("Implemented on child classes")

    def delete_parent(self, parentname):
        raise NotImplementedError("Implemented on child classes")

    def delete_child(self, parentname, childname):
        raise NotImplementedError("Implemented on child classes")

    def delete_children(self, parentname, childname, children):
        raise NotImplementedError("Implemented on child classes")
    
    def settings_writer(self, databaseparentname, databasechildname, storagefolder):
        
        data = {"parent": databaseparentname, "child": databasechildname, "storage": storagefolder}
        application_data = {"references": data}

        self.upload_data_all(application_data, "ApplicationSettings")