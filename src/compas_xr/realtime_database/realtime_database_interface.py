class RealtimeDatabaseInterface(object):
    
    def _construct_reference(self, project_name):
        raise NotImplementedError("Implemented on child classes")
    
    def _construct_child_refrence(self, parentname, childname):
        raise NotImplementedError("Implemented on child classes")
    
    def _construct_grandchild_refrence(self, parentname, childname, grandchildname):
        raise NotImplementedError("Implemented on child classes")
    
    def upload_data_to_reference(self, data, database_reference):
        raise NotImplementedError("Implemented on child classes")
    
    def get_data_from_reference(self, database_reference):
        raise NotImplementedError("Implemented on child classes")
    
    def delete_data_from_reference(self, database_reference):
        raise NotImplementedError("Implemented on child classes")
    
    def stream_data_from_reference(self, callback, database_reference):
        raise NotImplementedError("Implemented on child classes")

    def upload_data(self, data, project_name):
        database_reference = self._construct_reference(project_name)
        self.upload_data_to_reference(data, database_reference)

    def get_data(self, project_name):
        database_reference = self._construct_reference(project_name)
        return self.get_data_from_reference(database_reference)

    def upload_data_to_project(self, data, project_name, child_name):
        database_reference = self._construct_child_refrence(project_name, child_name)
        self.upload_data_to_reference(data, database_reference)

    def get_data_from_project(self, project_name, child_name):
        database_reference = self._construct_child_refrence(project_name, child_name)
        return self.get_data_from_reference(database_reference)
    
    def delete_data(self, project_name):
        database_reference = self._construct_reference(project_name)
        self.delete_data_from_reference(database_reference)
    
    def delete_data_from_project(self, project_name, child_name):
        database_reference = self._construct_child_refrence(project_name, child_name)
        self.delete_data_from_reference(database_reference)

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
    
    def application_settings_writer(self, databaseparentname, storagefolder="None", objorientation=True):
        
        data = {"parentname": databaseparentname, "storagename": storagefolder, "objorientation": objorientation}

        self.upload_data_all(data, "ApplicationSettings")