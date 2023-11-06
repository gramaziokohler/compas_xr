class StorageInterface(object):

    def upload_file(self, path_on_cloud, path_local):
        raise NotImplementedError("Implemented on child classes")

    def upload_data(self, path_on_cloud, data):
        raise NotImplementedError("Implemented on child classes")

    def download_file(self, path_on_cloud, path_local):
        raise NotImplementedError("Implemented on child classes")

    def get_data(self, path_on_cloud):
        raise NotImplementedError("Implemented on child classes")

    def upload_obj(self, path_on_cloud, cloud_folder, path_local):
        raise NotImplementedError("Implemented on child classes")

    def upload_objs(self, folder_local, cloud_folder_name):
        raise NotImplementedError("Implemented on child classes")
