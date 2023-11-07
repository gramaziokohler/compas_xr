
import os
from compas.datastructures import Assembly, Mesh
from compas.geometry import Transformation, Point, Vector, Frame
from compas_timber import assembly as TA
from compas.data import json_dumps,json_loads
from compas_xr.storage import Storage
from compas_xr.realtime_database import RealtimeDatabase

class AssemblyAssistant(object):

    # Class attribute for storage class instance? and RealtimeDatabase
    _shared_databaseinstance = None
    _shared_storageinstance = None

    def __init__(self, config=None):

        if config is not None:
            self._ensure_database(config)
            self._ensure_storage(config)
    
    #Internal Class functions for setting instance of database and storage_classes
    def _ensure_database(self, config):
        
        #Create shared instance of Database Class
        if not AssemblyAssistant._shared_databaseinstance: 
            database = RealtimeDatabase(config)
            AssemblyAssistant._shared_databaseinstance = database
                
        # Still no Database? Fail, we can't do anything
        if not AssemblyAssistant._shared_databaseinstance:
            raise Exception("Could not create instance of Database with path {}!".format(config))
        
        return AssemblyAssistant._shared_databaseinstance
    
    def _ensure_storage(self, config):
        
        #Create shared instance of Storage class        
        if not AssemblyAssistant._shared_storageinstance:    
            storage = Storage(config)
            AssemblyAssistant._shared_storageinstance = storage
        
        # Still no Storage? Fail, we can't do anything
        if not AssemblyAssistant._shared_storageinstance:
            raise Exception("Could not create instance of Storage with path {}!".format(config))
        
        return AssemblyAssistant._shared_storageinstance

    #Functions for adding and editing attributes to assemblies
    def add_assembly_attributes(self, assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        
        data_type_list = ['0.Cylinder','1.Box','2.ObjFile','3.Mesh']

        data = assembly.data
        graph = assembly.graph.data
        graph_node = graph["node"]

        for key in graph_node:
            graph_node[str(key)]['type_id'] = key
            graph_node[str(key)]['type_data'] = data_type_list[data_type]
            graph_node[str(key)]['is_built'] = False
            graph_node[str(key)]['is_planned'] = False
            graph_node[str(key)]['placed_by'] = "human"

        for k in robot_keys:
            graph_node[str(k)]['placed_by'] = "robot"

        if built_keys:
            for l in built_keys:
                graph_node[str(l)]['is_built'] = True

        if planned_keys:
            for m in planned_keys:
                graph_node[str(m)]['is_planned'] = True

        assembly = Assembly.from_data(data)
        print ("ASSEMBLY ATTRIBUTES ADDED")
        return assembly

    def add_assembly_attributes_timbers(self, assembly, data_type, robot_keys=None, built_keys=None, planned_keys=None):
        
        data_type_list = ['0.Cylinder','1.Box','2.ObjFile','3.Mesh']

        data = assembly.data
        beam_keys = assembly.beam_keys
        graph = assembly.graph.data
        graph_node = graph["node"]

        for key in beam_keys:
            graph_node[str(key)]['type_id'] = key
            graph_node[str(key)]['type_data'] = data_type_list[data_type]
            graph_node[str(key)]['is_built'] = False
            graph_node[str(key)]['is_planned'] = False
            graph_node[str(key)]['placed_by'] = "human"

        for k in robot_keys:
            if k in beam_keys:
                graph_node[str(k)]['placed_by'] = "robot"

        if built_keys:
            for l in built_keys:
                    if l in beam_keys:
                        graph_node[str(l)]['is_built'] = True

        if planned_keys:
            for m in planned_keys:
                    if m in beam_keys:
                        graph_node[str(m)]['is_planned'] = True

        timber_assembly = TA.assembly.TimberAssembly.from_data(data)
        print ("TIMBERS ASSEMBLY ATTRIBUTES ADDED")
        return timber_assembly

    def adjust_item_attributes(self, assembly, key, data_type, built_status, planning_status, placed_by):
        
        data_type_list = ['0.Cylinder','1.Box','2.ObjFile','3.Mesh']
        graph = assembly.graph.data
        graph_node = graph["node"]
        
        graph_node[key]['type_data'] = data_type_list[data_type]
        graph_node[key]['is_built'] = built_status
        graph_node[key]['is_planned'] = planning_status
        graph_node[key]['placed_by'] = placed_by

        data = graph_node[key]

        return assembly, data

    #Functions for uploading Assemblies to the Database and Storage    
    def upload_assembly_all_database(self, config, assembly, parentname): 

        #Ensure Database Instance
        self._ensure_database(config)

        #Get data from the assembly
        data = assembly.data
        
        #Database Reference
        database = AssemblyAssistant._shared_databaseinstance

        # Upload data using shared instance of the Database Class
        database.upload_data_all(data, parentname)
        print ("I think it worked")

    def upload_assembly_database(self, config, assembly, parentname, parentparamater, parameters):
        
        #Ensure Database Connection
        self._ensure_database(config)
        
        #Get data from the assembly
        data = assembly.data
        
        #Database Reference
        database = AssemblyAssistant._shared_databaseinstance
        
        parameters_list = {}

        paramaters_nested = {}
        
        for param in parameters:
            values = data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)
        parameters_list.update(paramaters_nested)

        #Upload
        database.upload_data_all(paramaters_nested, parentname)
        print("upload completed")

    def upload_assembly_aschild_database(self, config, assembly, parentname, childname, parentparameter, childparameter): 
        
        #Ensure Database Instance
        self._ensure_database(config)

        #Get data from the assembly
        data = assembly.data

        #Database Reference
        database = AssemblyAssistant._shared_databaseinstance

        #Get Assembly Information from Database
        assembly_info = data[parentparameter][childparameter]

        upload = database.upload_data_aschild(assembly_info, parentname, childname)

    def upload_assembly_aschildren_database(self, config, assembly, parentname, childname, parentparameter, childparameter, parameters):

        #Ensure Database Instance
        self._ensure_database(config)

        #Get data from the assembly
        data = assembly.data

        #Database Reference
        database = AssemblyAssistant._shared_databaseinstance

        for param in parameters:
            values = data[parentparameter][childparameter][param]
            database.upload_data_aschildren(values, parentname, childname, param)
        
    def upload_assembly_storage(self, config, path_on_cloud, assembly): 
        
        self._ensure_storage(config)
        
        # Shared storage instance with a specification of file name.
        storage = AssemblyAssistant._shared_storageinstance
        
        #Turn Assembly to data
        data = json_dumps(assembly, pretty=True)
        print ("uplode", type(data))

        #upload data to storage from the storage class method
        storage.upload_data(path_on_cloud, data)

    #Function for getting assemblies from Storage
    def get_assembly_storage(self, config, path_on_cloud):
        
        self._ensure_storage(config)
        
        # Shared storage instance with a specification of file name.
        storage = AssemblyAssistant._shared_storageinstance

        data = storage.get_data(path_on_cloud)
        
        #TODO: I am not sure why, but when I use the get data, this needs to happen twice for it to return an assembly
        assembly = json_loads(data)

        return assembly    

    #Function for Managing Assembly exports
    def export_timberassembly_objs(self, assembly, folder_path, new_folder_name):
        
        assembly_graph = assembly.graph.data
        nodes = assembly_graph["node"]
        assembly_beam_keys = assembly.beam_keys
        origin_frame = Frame(Point(0,0,0), Vector.Xaxis(), Vector.Yaxis())

        #Construct file path with the new folder name
        target_folder_path = os.path.join(folder_path, new_folder_name)
        
        #Make a folder with the folder name if it does not exist
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)
        
        #Iterate through assembly beams and perform transformation and export
        for key in assembly_beam_keys:
            beam = nodes[str(key)]["part"]
            frame = beam.frame
            
            #Extract compas box from beam
            beam_box = beam.shape
            
            #Create Transformation from beam frame to world_xy frame and maybe a copy?
            transformation = Transformation.from_frame_to_frame(frame, origin_frame)
            
            #Transform box from frame to world xy
            box_transformed = beam_box.transformed(transformation)
            
            #Get all information from the box and convert to mesh
            box_vertices = box_transformed.vertices
            box_faces = box_transformed.faces
            box_mesh = Mesh.from_vertices_and_faces(box_vertices, box_faces)
            
            # Mesh to obj with file name being KEY and folder being the newly created folder
            if os.path.exists(target_folder_path):
                file_name = str(key)+".obj"
                obj_file_path = os.path.join(target_folder_path, file_name)
                box_mesh.to_obj(obj_file_path)
            
            else:
                raise Exception("File path does not exist {}".format(target_folder_path))