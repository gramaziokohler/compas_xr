import os

from compas.datastructures import Mesh
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Transformation
from compas.geometry import Vector
from compas_model.elements import Element
from compas_model.models import Model
from compas_timber.model import TimberModel


class ModelExtensions:
    """Additional export and localization helpers for COMPAS models."""

    def export_timber_model_objs(self, model: TimberModel, folder_path: str, new_folder_name: str, z_to_y_remap: bool = False) -> None:
        """Export timber model beams as OBJ files."""
        target_folder_path = os.path.join(folder_path, new_folder_name)
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        if z_to_y_remap:
            frame = Frame(Point(0, 0, 0), Vector.Xaxis(), Vector.Zaxis())
        else:
            frame = Frame.worldXY()

        for beam in model.beams:
            brep_meshes = beam.modelgeometry.to_meshes()
            compas_mesh = Mesh()
            for mesh in brep_meshes:
                compas_mesh.join(mesh)
            mesh_transformed = compas_mesh.transformed(Transformation.from_frame_to_frame(Frame.worldXY(), frame))

            filename = "{}.obj".format(str(beam.guid))
            mesh_transformed.to_obj(os.path.join(target_folder_path, filename))

    def export_mesh_model_objs(self, model: Model, folder_path: str, new_folder_name: str, z_to_y_remap: bool = False) -> None:
        """Export the mesh geometry of every element in a model as an OBJ file."""
        target_folder_path = os.path.join(folder_path, new_folder_name)
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        transformation = None
        if z_to_y_remap:
            target_frame = Frame(Point(0, 0, 0), Vector.Xaxis(), Vector.Zaxis())
            transformation = Transformation.from_frame_to_frame(Frame.worldXY(), target_frame)

        for element in model.elements():
            mesh = element.modelgeometry
            if transformation:
                mesh = mesh.transformed(transformation)

            filename = "{}.obj".format(str(element.guid))
            mesh.to_obj(os.path.join(target_folder_path, filename))

    def create_qr_model(self, qr_frames: list[Frame]) -> Model:
        """Create a model containing one named element for every localization frame."""
        model = Model()
        for index, frame in enumerate(qr_frames):
            element = Element(name="QR_{}".format(index), transformation=Transformation.from_frame(frame))
            model.add_element(element)
        return model
