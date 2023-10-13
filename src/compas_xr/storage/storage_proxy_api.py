from compas_xr.storage.storage_pyrebase import Storage


#TODO: Converting Functions from class to proxy functions, but would prefer to work with .net framework

def upload_file(path_on_cloud, path_local, config_file=None):
    storage = Storage(config_file)
    storage.upload_file(path_on_cloud, path_local)

def download_file(path_on_cloud, path_local, config_file=None):
    storage = Storage(config_file)
    print("path_on_cloud", path_on_cloud)
    print(path_local)
    storage.download_file(path_on_cloud, path_local)
    print("done")
