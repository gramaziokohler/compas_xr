from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.topology import breadth_first_ordering
from compas.datastructures import Graph

from compas_xr.files.usd import USDScene
from compas_xr.files.gltf import GLTFScene


__all__ = ["Scene"]


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

    @property
    def data(self):
        data_dict = super(Scene, self).data
        data_dict["materials"] = [m.data for m in self.materials]
        return data_dict

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


if __name__ == "__main__":
    import os
    from compas.geometry import Box
    from compas.geometry import Frame, Rotation, Vector
    from compas_xr import DATA
    from compas_xr.datastructures import Material
    from compas_xr.datastructures.material import PBRMetallicRoughness

    scene = Scene()
    world = scene.add_layer("world")

    material = Material(name="material")
    material.pbr_metallic_roughness = PBRMetallicRoughness()
    material.pbr_metallic_roughness.base_color_factor = [0.9, 0.4, 0.2, 1.0]
    material.pbr_metallic_roughness.metallic_factor = 0.0
    material.pbr_metallic_roughness.roughness_factor = 0.5
    mkey = scene.add_material(material)

    # frame = Frame.worldXY()
    # frame.point = [1, 2, 3]
    # frame = Frame.from_euler_angles([0.1, 0.2, 0.3], point=[1, 2, 3])

    rotation = Rotation.from_basis_vectors(Vector(0.936, 0.275, -0.218), Vector(-0.274, 0.961, 0.037))
    frame = Frame.from_rotation(rotation, point=[1, 2, 3])
    box = Box(frame, 1, 1, 1)
    scene.add_layer("box", parent=world, element=box, material=mkey)  # material_key=mkey
    # TODO: materials_map?

    scene_data_before = scene.data

    usd_filename = os.path.join(DATA, "test_scene.usda")
    gltf_filename = os.path.join(DATA, "test_scene.gltf")

    scene.to_usd(usd_filename)
    scene.to_gltf(gltf_filename)

    scene = Scene.from_usd(usd_filename)
    print("USD")
    print("=======================")
    print(scene.data)

    """

    scene = Scene.from_gltf(gltf_filename)
    print("GLTF")
    print("=======================")
    print(scene.data)

    scene_data_after = scene.data

    print(scene_data_before["node"])
    print(scene_data_after["node"])

    assert scene_data_before["materials"] == scene_data_after["materials"]
    assert scene_data_before["attributes"] == scene_data_after["attributes"]
    assert scene_data_before["dna"] == scene_data_after["dna"]
    assert scene_data_before["dea"] == scene_data_after["dea"]
    assert scene_data_before["adjacency"] == scene_data_after["adjacency"]
    assert scene_data_before["edge"] == scene_data_after["edge"]
    """
