
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from compas.datastructures import Mesh
from compas.datastructures.network.core import Graph

from compas.geometry import Rotation
from compas.geometry import Box

from compas.files import GLTFContent
from compas.files import GLTFExporter

from compas_xr.usd import prim_from_box
from compas_xr.usd import prim_from_mesh
from compas_xr.usd import prim_default
from compas_xr.usd import prim_instance
from compas_xr.usd import reference_filename

__all__ = [
    'Scene',
    'Animation'
]


class Scene(Graph):  # or scenegraoh
    """Class for managing a Scene.


    Attributes
    ----------
    """

    def __init__(self, name="scene", up_axis="Z"):
        super(Scene, self).__init__()
        self.name = name
        self.up_axis = up_axis
        self.update_default_node_attributes({'is_reference': False})

    @classmethod
    def from_gltf(cls, filepath):
        raise NotImplementedError

    @classmethod
    def from_usd(cls, filepath):
        raise NotImplementedError

    def to_gltf(self, filepath, embed_data=False):
        """
        """

        content = GLTFContent()
        scene = content.add_scene(self.name)

        def get_node_by_name(content, name):  # TODO: upstream to GLTF
            for key in content.nodes:
                if content.nodes[key].name == name:
                    return content.nodes[key]
            return None

        for key in self.node:

            parent = self.node_attribute(key, 'parent')
            is_reference = self.node_attribute(key, 'is_reference')
            frame = self.node_attribute(key, 'frame')
            element = self.node_attribute(key, 'element')
            instance_of = self.node_attribute(key, 'instance_of')

            if not parent:
                node = content.add_node_to_scene(scene, node_name=key)
            else:
                parent = get_node_by_name(content, parent)
                node = content.add_child_to_node(parent, key)

            if frame:
                node.translation = list(frame.point)
                node.rotation = list(Rotation.from_frame(frame).quaternion.xyzw)

            if instance_of:
                reference = get_node_by_name(content, instance_of)
                node.mesh_key = reference.mesh_key
            elif is_reference:
                # set invisible?
                pass

            if element:
                mesh = Mesh.from_shape(element)  # if shape, else take Mesh directly
                mesh.quads_to_triangles()
                content.add_mesh_to_node(node, mesh)

        exporter = GLTFExporter(filepath, content, embed_data=True)
        exporter.export()

    def to_usd(self, filepath):
        from pxr import Usd
        from pxr import UsdGeom

        stage = Usd.Stage.CreateNew(filepath)

        UsdGeom.SetStageUpAxis(stage, "Z")  # take the one which is in stage

        for key in self.node:

            parent = self.node_attribute(key, 'parent')
            is_reference = self.node_attribute(key, 'is_reference')
            frame = self.node_attribute(key, 'frame')
            element = self.node_attribute(key, 'element')
            instance_of = self.node_attribute(key, 'instance_of')

            is_root = True if not parent else False
            if parent:
                layers = [parent]
                while self.node[parent]['parent']:
                    parent = self.node[parent]['parent']
                    layers.append(parent)
                layers.reverse()
                layers.append(key)
                path = '/' + '/'.join(layers)
            else:
                path = '/%s' % key

            # print(path)

            if is_reference:
                # we have to create a reference file
                scene_reference = Scene()
                scene_reference.add_node('world', parent=None)
                scene_reference.add_node(key, element=element, parent='world')  # more attr?
                reference_filepath = reference_filename(stage, key, fullpath=True)
                scene_reference.to_usd(reference_filepath)

            else:
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

                    if element:
                        if type(element) == Box:
                            prim = prim_from_box(stage, path, element)
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
