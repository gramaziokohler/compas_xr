class StorageInterface(object):
    def download_file(self, path_on_cloud, path_local):
        raise NotImplementedError("Implemented on child classes")

    def upload_file(self, path_on_cloud, path_local):
        raise NotImplementedError("Implemented on child classes")
