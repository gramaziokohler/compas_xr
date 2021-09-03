
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from compas.datastructures import Mesh
from compas.datastructures.network.core import Graph

from compas.geometry import Box

from compas.topology import breadth_first_ordering

from compas.files import GLTFContent
from compas.files import GLTFExporter

from compas_xr.usd import prim_from_box
from compas_xr.usd import prim_from_mesh
from compas_xr.usd import prim_default
from compas_xr.usd import prim_instance
from compas_xr.usd import reference_filename


from .gltf_helpers import gltf_add_node_to_content
from .gltf_helpers import gltf_add_material_to_content


__all__ = [
    'Scene',
    'Animation'
]


class Scene(Graph):  # or scenegraoh
    """Class for managing a Scene.


    Attributes
    ----------
    """

    def __init__(self, name="scene", up_axis="Z", materials=None):
        super(Scene, self).__init__()
        self.name = name
        self.up_axis = up_axis
        self.update_default_node_attributes({'is_reference': False})
        self.materials = materials or []

    def add_layer(self, key, parent=None, attr_dict=None, **kwattr):
        self.add_node(key, parent=parent, attr_dict=attr_dict, **kwattr)
        # raise if parent does not exist
        if parent:
            self.add_edge(parent, key)
        return key

    @classmethod
    def from_gltf(cls, filepath):
        raise NotImplementedError

    @classmethod
    def from_usd(cls, filepath):
        raise NotImplementedError

    @property
    def ordered_keys(self):
        for root in self.nodes_where({'parent': None}):
            for key in breadth_first_ordering(self.adjacency, root):
                yield key

    def node_to_root(self, key):
        shortest_path = [key]
        parent = self.node_attribute(key, 'parent')
        while parent:
            shortest_path.append(parent)
            key = parent
            parent = self.node_attribute(key, 'parent')
        return shortest_path

    def to_gltf(self, filepath, embed_data=False):
        """
        """
        content = GLTFContent()
        scene = content.add_scene(self.name)

        for material in self.materials:
            gltf_add_material_to_content(content, material)

        # 1. Add those that are references first
        visited = []
        for key in self.nodes_where({'is_reference': True}):
            shortest_path = self.node_to_root(key)
            for key in reversed(shortest_path):
                if key not in visited:
                    gltf_add_node_to_content(self, content, scene, key)
                    visited.append(key)

        for key in self.ordered_keys:
            if key not in visited:
                gltf_add_node_to_content(self, content, scene, key)

        exporter = GLTFExporter(filepath, content, embed_data=True)
        exporter.export()

    def to_usd(self, filepath):
        from pxr import Usd
        from pxr import UsdGeom

        stage = Usd.Stage.CreateNew(filepath)

        UsdGeom.SetStageUpAxis(stage, "Z")  # take the one which is in stage

        # 1. Add those that are references first
        for key in self.nodes_where({'is_reference': True}):
            element = self.node_attribute(key, 'element')
            scene_reference = Scene()
            scene_reference.add_layer('world', parent=None)
            scene_reference.add_layer(key, parent='world', element=element)  # more attr?
            reference_filepath = reference_filename(stage, key, fullpath=True)
            scene_reference.to_usd(reference_filepath)

        for key in self.ordered_keys:

            parent = self.node_attribute(key, 'parent')
            is_reference = self.node_attribute(key, 'is_reference')
            frame = self.node_attribute(key, 'frame')
            element = self.node_attribute(key, 'element')
            instance_of = self.node_attribute(key, 'instance_of')

            is_root = True if not parent else False
            path = '/' + '/'.join(reversed(self.node_to_root(key)))

            if not is_reference:
                # if there is a frame in the node, we first have to add Xform

                if instance_of:
                    if frame:
                        prim_default(stage, path, frame)
                        path += '/element'
                    prim = prim_instance(stage, path, self.node_attribute(key, 'instance_of'))
                    # if frame:
                    #    apply_frame_transformation_on_prim(ref, frame)

                else:

                    if frame:
                        prim = prim_default(stage, path, frame)
                        path += '/element'

                    #print("path", path)
                    if element:
                        if type(element) == Box:
                            prim = prim_from_box(stage, path, element)
                            # prim = prim_from_mesh(stage, path, Mesh.from_shape(element))
                        elif type(element) == Mesh:
                            prim = prim_from_mesh(stage, path, element)
                        else:
                            raise NotImplementedError

                    if not frame and not element:
                        prim = prim_default(stage, path)

            if is_root:
                stage.SetDefaultPrim(prim.GetPrim())

        stage.GetRootLayer().Save()


class Animation(object):
    pass
