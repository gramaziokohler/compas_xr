from compas_xr.realtime_database.realtime_database_pyrebase import RealtimeDatabase

def dummy(config_file=None):
    database = RealtimeDatabase(config_file)
    messgae = database.dummy()
    return messgae

def set_json_data(json_f, parentname, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("json_file", json_f)
    print ("parentname", parentname)
    database.set_json_data(json_f, parentname)
    print ("done")

def set_json_data_keys(json_f, parentname, keys, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("json_file", json_f)
    print ("parentname", parentname)
    print ("keys", keys)
    database.set_json_data_keys(json_f, parentname, keys)
    print("done")

def set_data(parentname, data, config_file):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    database.set_data(parentname, data)
    print ("done")
    
def set_data_keys(parentname, data, keys, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    print ("data_type", type(data))
    print ("keys", keys)
    database.set_data_keys(parentname, data, keys)
    print ("done")
    
def set_assembly(parentname, assembly, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    print ("assembly_type", type(assembly))
    database.set_assembly(parentname, assembly)
    print ("done")

def set_assembly_keys(parentname, assembly, keys, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    print ("assembly_type", type(assembly))
    print ("keys", keys)
    database.set_assembly_keys(parentname, assembly, keys)
    print ("done")

def set_assembly_keys_timbers(parentname, assembly, keys, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    print ("assembly_type", type(assembly))
    print ("keys", keys)
    database.set_assembly_keys_timbers(parentname, assembly, keys)

def add_assembly_attributes(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("data_type", data_type)
    print ("robot_keys", robot_keys)
    print ("built_keys", built_keys)
    print ("planned_keys", planned_keys)
    database.add_assembly_attributes(assembly, data_type, robot_keys, built_keys, planned_keys)
    print ("done")

def add_assembly_attributes_timbers(assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("data_type", data_type)
    print ("robot_keys", robot_keys)
    print ("built_keys", built_keys)
    print ("planned_keys", planned_keys)
    database.add_assembly_attributes_timbers(assembly, data_type, robot_keys, built_keys, planned_keys)
    print ("done")

def remove_parent(parentname, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    database.remove_parent(parentname)
    print ("done")

def remove_child(parentname, childname, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    print ("childname", childname)
    database.remove_child(parentname, childname)
    print ("done")

def remove_children(parentname, children, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    print ("childeren", children)
    database.remove_children(parentname, children)
    print ("done")

def get_json_data_child(parentname, childname, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    print ("childname", childname)
    database.get_json_data_child(parentname, childname)
    print ("done")

def get_json_data_parent(parentname, config_file=None):
    database = RealtimeDatabase(config_file)
    print ("parentname", parentname)
    database.get_json_data_parent(parentname)
    print ("done")

