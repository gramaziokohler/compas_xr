from compas_xr.storage.storage_pyrebase import Storage


#TODO: Converting Functions from class to proxy functions, but would prefer to work with .net framework instead of this

def upload_file(path_on_cloud, path_local, config_file=None):
    storage = Storage(config_file)
    storage.upload_file(path_on_cloud, path_local)

def download_file(path_on_cloud, path_local, config_file=None):
    storage = Storage(config_file)
    print("path_on_cloud", path_on_cloud)
    print("path_local", path_local)
    storage.download_file(path_on_cloud, path_local)
    print("done")

#TODO: Test these functions
def add_assembly_attributes(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None, config_file=None):
    storage = Storage(config_file)
    storage.add_assembly_attributes(assembly, data_type, robot_keys, built_keys, planned_keys)
    
def add_assembly_attributes_timbers(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None, config_file=None):
    storage = Storage(config_file)
    storage.add_assembly_attributes_timbers(assembly, data_type, robot_keys, built_keys, planned_keys)

def upload_data(path_on_cloud, data, config_file=None):
    storage = Storage(config_file)
    print ("path_on_cloud", path_on_cloud)
    storage.upload_data(path_on_cloud, data)
    print ("done")

def download_data(path_on_cloud, path_local, config_file=None):
    storage = Storage(config_file)
    print("path_on_cloud", path_on_cloud)
    print("path_local", path_local)
    data = storage.download_data(path_on_cloud, path_local)
    return data

def upload_assembly(path_on_cloud, assembly, config_file=None):
    stoarge = Storage(config_file)
    print("path_on_cloud", path_on_cloud)
    stoarge.upload_assembly(path_on_cloud, assembly)
    print ("done")

def download_assembly(path_on_cloud, path_local, assembly, config_file=None):
    stoarge = Storage(config_file)
    print("path_on_cloud", path_on_cloud)
    print("path_local", path_local)
    assembly = stoarge.upload_assembly(path_on_cloud, assembly)
    return assembly    