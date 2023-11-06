
from compas.datastructures import Assembly, Mesh
from compas.geometry import Transformation, Point, Vector, Frame
from compas_timber import assembly as TA

class AssemblyDirector(object):

    # Class attribute for storage class instance? and RealtimeDatabase
    _shared_database = None
    _shared_storage = None

    def __init__(self):
        pass
        # self.config_path = config_path
        # self._guid = None
        # self._ensure_database()
    
    def _ensure_database(self, config):
        pass

    def _ensure_storage(self, config):
        pass

    #Functions for adding attributes to assemblies
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

        return timber_assembly
    
        #TODO: NEEDS TO BE MOVED
    
    def upload_assembly_all_database(self, assembly, parentname):

        #Ensure Database Connection
        self._ensure_database()

        data = assembly.data
        serialized_data = json_dumps(data)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            print ("inside of begin upload")
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            print (uploadtask)
            task_upload = uploadtask.GetAwaiter()
            print (task_upload)
            task_upload.OnCompleted(lambda: result["event"].set())
            print
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print (upload)

    def upload_assembly_database(self, assembly, parentname, parentparamater, parameters):
        
        #Ensure Database Connection
        self._ensure_database()

        data = assembly.data
        
        parameters_list = {}

        paramaters_nested = {}
        
        for param in parameters:
            print (param)
            values = data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)
        parameters_list.update(paramaters_nested)

        serialized_data = json_dumps(parameters_list)
        database_reference = RealtimeDatabase._shared_database 

        def _begin_upload(result):
            uploadtask = database_reference.Child(parentname).PutAsync(serialized_data)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())
            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)
        print (upload)

    def upload_assembly_storage(self, path_on_cloud, assembly):
        
        self._ensure_storage()
        
        # Shared storage instance with a specification of file name.
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)
            
        data = json_dumps(assembly, pretty=True)

        byte_data = Encoding.UTF8.GetBytes(data)
        stream = MemoryStream(byte_data)

        def _begin_upload(result):

            uploadtask = storage_refrence.PutAsync(stream)
            task_upload = uploadtask.GetAwaiter()
            task_upload.OnCompleted(lambda: result["event"].set())

            result["event"].wait()
            result["data"] = True
        
        upload = self._start_async_call(_begin_upload)

    #TODO: Can simply just call get data function from storage... not sure if it needs to be duplicated as get assembly or just use get_data
    def get_assembly_storage(self, path_on_cloud):
        
        self._ensure_storage()
        
        # Shared storage instance with a specificatoin of file name.
        storage_refrence = Storage._shared_storage.Child(path_on_cloud)
        print (storage_refrence)

        def _begin_download(result):
            downloadurl_task = storage_refrence.GetDownloadUrlAsync()
            task_download = downloadurl_task.GetAwaiter()
            task_download.OnCompleted(lambda: result["event"].set())

            result["event"].wait()
            result["data"] = downloadurl_task.Result
        
        url = self._start_async_call(_begin_download)

        data = self._get_file_from_remote(url)

        desearialized_data = json_loads(data)

        return desearialized_data    

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