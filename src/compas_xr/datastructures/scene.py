from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.topology import breadth_first_ordering
from compas.datastructures import Graph

from compas_xr.files.usd import USDScene
from compas_xr.files.gltf import GLTFScene


__all__ = ["Scene", "Animation"]


class Scene(Graph):  # or scenegraph
    """Class for managing a Scene.


    Attributes
    ----------
    """

    def __init__(self, name="scene", up_axis="Z", materials=None):
        super(Scene, self).__init__()
        self.name = name
        self.up_axis = up_axis
        self.update_default_node_attributes({"is_reference": False})
        self.materials = materials or []

    def add_layer(self, key, parent=None, attr_dict=None, **kwattr):
        self.add_node(key, parent=parent, attr_dict=attr_dict, **kwattr)
        # raise if parent does not exist
        if parent:
            self.add_edge(parent, key)
        return key

    def add_material(self, material):
        self.materials.append(material)
        return len(self.materials) - 1

    # @property
    # def data(self):
    #    data_dict = super(Scene, self).data
    #    data_dict['materials'] = [m.data for m in self.materials]
    #    return data_dict

    @classmethod
    def from_gltf(cls, filepath):
        return GLTFScene.from_gltf(filepath).to_compas()

    @classmethod
    def from_usd(cls, filepath):
        return USDScene.from_usd(filepath).to_compas()

    @property
    def ordered_keys(self):
        for root in self.nodes_where({"parent": None}):
            for key in breadth_first_ordering(self.adjacency, root):
                yield key

    def node_to_root(self, key):
        shortest_path = [key]
        parent = self.node_attribute(key, "parent")
        while parent:
            shortest_path.append(parent)
            key = parent
            parent = self.node_attribute(key, "parent")
        return shortest_path

    def to_usd(self, filepath):
        USDScene.from_scene(self).to_usd(filepath)

    def to_gltf(self, filepath, embed_data=False):
        GLTFScene.from_scene(self).to_gltf(filepath, embed_data=embed_data)

    def subscene(self, key):
        subscene = Scene()

        def _add_branch(scene, key, parent):
            element = self.node_attribute(key, "element")
            # TODO: what to do if we have another reference?
            scene.add_layer(key, parent=parent, element=element)  # more attr?
            for child in self.nodes_where({"parent": key}):
                _add_branch(scene, child, key)

        _add_branch(subscene, key, None)
        return subscene

    def _all_children(self, key, include_key=True):
        def children(key, array):
            array.append(key)
            for child in self.nodes_where({"parent": key}):
                children(child, array)

        array = []
        children(key, array)
        if not include_key:
            array = array[1:]
        return array


class Animation(object):
    pass


if __name__ == "__main__":
    scene = Scene()
    world = scene.add_node("world")
    scene.add_node("element", parent=world)

    scene.add_node("element", parent=None)
    print(scene.data)
