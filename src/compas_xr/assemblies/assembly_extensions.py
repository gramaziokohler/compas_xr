import os
# from Rhino.Geometry import Mesh, MeshingParameters
from compas.datastructures import Assembly, Mesh
from compas.geometry import Transformation, Point, Vector, Frame
from compas_timber import assembly as TA
from compas_timber.consumers import BrepGeometryConsumer

class AssemblyExtensions(object):

    def __init__(self):
        pass
    
    #Function for Managing Assembly exports
    def export_timberassembly_objs(self, assembly, folder_path, new_folder_name, z_to_y_remap=False):

        #Construct file path with the new folder name
        target_folder_path = os.path.join(folder_path, new_folder_name)
        
        #Make a folder with the folder name if it does not exist
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        #Create frame options for orientation of objects
        if z_to_y_remap:
            frame = Frame(Point(0,0,0), Vector.Xaxis(), Vector.Zaxis())
        else:
            frame = Frame.worldXY()
        
        #Loop through the geometry from the Brep Consumer
        for result in BrepGeometryConsumer(assembly).result:
            brep = result.geometry
            beam_frame = result.beam.frame
            key = result.beam.key

            brep_meshes = brep.to_meshes()
            compas_mesh = Mesh()
            for mesh in brep_meshes:
                compas_mesh.join(mesh)

            compas_mesh.transform(Transformation.from_frame_to_frame(beam_frame, frame))
                        
            # Mesh to obj with file name being KEY and folder being the newly created folder
            if os.path.exists(target_folder_path):
                compas_mesh.to_obj(r"{}\{}.obj".format(target_folder_path, str(key)))
            
            #Raise Exception if the target folder does not exist.
            else:
                raise Exception("File path does not exist {}".format(target_folder_path))

    #Function for Managing Assembly exports
    def export_assembly_objs(self, assembly, folder_path, new_folder_name):
        
        assembly_graph = assembly.graph.__data__
        nodes = assembly_graph["node"]
        z_to_y_mapped_frame = Frame(Point(0,0,0), Vector.Xaxis(), Vector.Zaxis())

        #Construct file path with the new folder name
        target_folder_path = os.path.join(folder_path, new_folder_name)

        #Make a folder with the folder name if it does not exist
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        #Iterate through assembly and perform transformation and export
        for key in nodes:
            
            #extract part
            part = nodes[str(key)]["part"]
            
            frame = part.frame
            
            #Create Transformation from beam frame to world_xy frame and maybe a copy?
            transformation = Transformation.from_frame_to_frame(frame, z_to_y_mapped_frame)
            
            #Transform box from frame to world xy
            part_transformed = part.transformed(transformation)
            
            if nodes[str(key)]["type_data"] in ["0.Cylinder", "1.Box"]:
                part_vert, part_faces = part_transformed.to_vertices_and_faces()
                mesh = Mesh.from_vertices_and_faces(part_vert, part_faces)
            
            elif nodes[str(key)]["type_data"] == "3.Mesh":
                mesh = part_transformed
            
            #TODO: what should I do with .obj, also not sure if this needs to be here or if we just make it from assembly data.

            #Mesh to obj with file name being KEY and folder being the newly created folder
            if os.path.exists(target_folder_path):
                file_name = str(key)+".obj"
                obj_file_path = os.path.join(target_folder_path, file_name)
                mesh.to_obj(obj_file_path)
            
            else:
                raise Exception("File path does not exist {}".format(target_folder_path))