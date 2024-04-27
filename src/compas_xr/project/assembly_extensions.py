import os

from compas.datastructures import Assembly
from compas.datastructures import Mesh
from compas.datastructures import Part
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Transformation
from compas.geometry import Vector
from compas_timber.consumers import BrepGeometryConsumer


class AssemblyExtensions(object):
    """
    AssemblyExtensions is a class for extending the functionality of the compas.datastructures.Assembly class.

    The AssemblyExtensions class provides additional functionalities such as exporting parts as .obj files
    and creating a frame assembly from a list of compas.geometry.Frames with a specific data structure for localization information.

    """

    def export_timberassembly_objs(self, assembly, folder_path, new_folder_name, z_to_y_remap=False):
        """
        Export timber assembly beams as .obj files to a folder path.

        Parameters
        ----------
        assembly : compas_timber.assembly.TimberAssembly
            The assembly that you want to export beams from.
        folder_path : str
            The path in which you would like to create a storage folder.
        new_folder_name : str
            The name of the folder you would like to create.
        z_to_y_remap : bool, optional
            A boolean that determines if the z-axis should be remapped to the y-axis for .obj export. Default is False.

        Returns
        -------
        None

        """
        target_folder_path = os.path.join(folder_path, new_folder_name)
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        if z_to_y_remap:
            frame = Frame(Point(0, 0, 0), Vector.Xaxis(), Vector.Zaxis())
        else:
            frame = Frame.worldXY()

        for result in BrepGeometryConsumer(assembly).result:
            brep = result.geometry
            beam_frame = result.beam.frame
            key = result.beam.key

            brep_meshes = brep.to_meshes()
            compas_mesh = Mesh()
            for mesh in brep_meshes:
                compas_mesh.join(mesh)
            mesh_transformed = compas_mesh.transformed(Transformation.from_frame_to_frame(beam_frame, frame))

            if not os.path.exists(target_folder_path):
                raise Exception("File path does not exist {}".format(target_folder_path))
            filename = "{}.obj".format(str(key))
            mesh_transformed.to_obj(os.path.join(target_folder_path, filename))

    def export_mesh_assembly_objs(self, assembly, folder_path, new_folder_name, z_to_y_remap=False):
        """
        Export Mesh assembly parts as .obj files to a folder path.

        Parameters
        ----------
        assembly : compas.datastructures.Assembly
            The Mesh (compas.datastructures.Mesh) assembly that you want to export parts from.
        folder_path : str
            The path in which you would like to create a storage folder.
        new_folder_name : str
            The name of the folder you would like to create.
        z_to_y_remap : bool, optional
            A boolean that determines if the z-axis should be remapped to the y-axis for .obj export. Default is False.

        Returns
        -------
        None

        """
        target_folder_path = os.path.join(folder_path, new_folder_name)
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        if z_to_y_remap:
            frame = Frame(Point(0, 0, 0), Vector.Xaxis(), Vector.Zaxis())
        else:
            frame = Frame.worldXY()

        for part in assembly.parts():
            # Mesh assembly can be made with or without a frame (ex. assembly.add_part(Mesh)) try & default to worldXY
            try:
                part_frame = part.frame
            except:
                part_frame = Frame.worldXY()
            part_transformed = part.transformed(Transformation.from_frame_to_frame(part_frame, frame))

            if not os.path.exists(target_folder_path):
                raise Exception("File path does not exist {}".format(target_folder_path))
            filename = "{}.obj".format(str(part.key))
            part_transformed.to_obj(os.path.join(target_folder_path, filename))

    def create_qr_assembly(self, qr_frames):
        """
        Create a frame assembly from a list of compas.geometry.Frames with a specific data structure for localization data.

        Parameters
        ----------
        qr_frames : list of 'compas.geometry.Frame'
            A list of frames at specific locations for application localization data.

        Returns
        -------
        :class: 'compas.datastructures.Assembly'
            The constructed database reference.

        """
        assembly = Assembly()
        for frame in qr_frames:
            part = Part(frame, frame=frame)
            assembly.add_part(part)
        return assembly
