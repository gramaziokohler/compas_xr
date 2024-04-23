import os
# from Rhino.Geometry import Mesh, MeshingParameters
from compas.datastructures import Assembly, Mesh
from compas.geometry import Transformation, Point, Vector, Frame
from compas_timber.consumers import BrepGeometryConsumer

class AssemblyExtensions(object):

    def __init__(self):
        pass
    
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

    def export_mesh_assembly_objs(self, assembly, folder_path, new_folder_name, z_to_y_remap=False):
        
        
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

        #TODO: CONFIRM TRY EXCEPT BLOCK WITH GONZALO.
        for part in assembly.parts():
            try:
                part_frame = part.frame
            except:
                part_frame = Frame.worldXY()
            
            #Transform mesh part from frame to to frame
            part_transformed = part.transformed(Transformation.from_frame_to_frame(part_frame, frame))
            
            # Mesh to obj with file name being KEY and folder being the newly created folder
            if os.path.exists(target_folder_path):
                part_transformed.to_obj(r"{}\{}.obj".format(target_folder_path, str(part.key)))
            
            else:
                raise Exception("File path does not exist {}".format(target_folder_path))