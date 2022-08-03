from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas
from compas.topology import breadth_first_ordering
from compas.datastructures import Graph

if not compas.IPY:
    from compas_xr.conversions.usd import USDScene
from compas_xr.conversions.gltf import GLTFScene
from compas_xr.utilities import argsort

from .material import Image
from .material import Texture
from .material import Material

__all__ = ["Scene"]


class Scene(Graph):  # or scenegraph
    """Class for managing a Scene.


    Attributes
    ----------
    """

    def __init__(self, name="scene", up_axis="Z", materials=None, images=None, textures=None):
        super(Scene, self).__init__()
        self.name = name
        self.up_axis = up_axis
        self.update_default_node_attributes({"is_reference": False})
        self.materials = materials or []
        self.images = images or []
        self.textures = textures or []

    def add_layer(self, key, parent=None, attr_dict=None, **kwattr):
        self.add_node(key, parent=parent, attr_dict=attr_dict, **kwattr)
        # raise if parent does not exist
        if parent:
            self.add_edge(parent, key)
        return key

    def has_layer(self, key):
        return self.has_node(key)

    def unique_key(self, name, num_padding=3, i=0):
        if not self.has_node(name):
            return name
        postfix = "%0" + str(num_padding) + "d"
        key = (name + postfix) % (i)
        while self.has_node(key):
            i += 1
            key = (name + postfix) % (i)
        return key

    def add_material(self, material):
        self.materials.append(material)
        return len(self.materials) - 1

    def add_image(self, image):
        self.images.append(image)
        return len(self.images) - 1

    def add_texture(self, texture):
        self.textures.append(texture)
        return len(self.textures) - 1

    @property
    def has_references(self):
        """Returns `True` if the scene contains references, `False` otherwise."""
        references = list(self.nodes_where({"is_reference": True}))
        return bool(len(references))

    @property
    def ordered_references(self):
        # Go through references and add those with the deepest depth first
        block_names = []
        block_depths = []

        def add_key_and_depth(key, depth, block_names, block_depths):
            if key not in block_names:
                block_names.append(key)
                block_depths.append(depth)
            else:
                idx = block_names.index(key)
                if block_depths[idx] < depth:
                    block_depths[idx] = depth

        def find_references_recursive(key, depth, block_names, block_depths):
            for child in self.nodes_where({"parent": key}):
                if self.node_attribute(child, "instance_of"):
                    instance = self.node_attribute(child, "instance_of")
                    add_key_and_depth(instance, depth + 1, block_names, block_depths)
                    find_references_recursive(instance, depth + 1, block_names, block_depths)
                else:
                    find_references_recursive(child, depth + 1, block_names, block_depths)

        depth = 0
        for key in self.nodes_where({"is_reference": True}):
            add_key_and_depth(key, depth, block_names, block_depths)
            find_references_recursive(key, depth, block_names, block_depths)

        for idx in reversed(argsort(block_depths)):
            yield block_names[idx]

    @property
    def data(self):
        data = super(Scene, self).data
        if self.materials is not None:
            data["materials"] = [m.data for m in self.materials]
        if self.images is not None:
            data["images"] = [m.data for m in self.images]
        if self.textures is not None:
            data["textures"] = [m.data for m in self.textures]
        return data

    @data.setter
    def data(self, data):
        super(Scene, self.__class__).data.fset(self, data)
        if data.get("materials") is not None:
            self.materials = [Material.from_data(d) for d in data.get("materials")]
        if data.get("images") is not None:
            self.images = [Image.from_data(d) for d in data.get("images")]
        if data.get("textures") is not None:
            self.textures = [Texture.from_data(d) for d in data.get("textures")]

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
        USDScene.from_scene(self, filepath).to_usd(filepath)

    def to_gltf(self, filepath, embed_data=False):
        GLTFScene.from_scene(self).to_gltf(filepath, embed_data=embed_data)

    def subscene(self, key):
        subscene = Scene()
        world = subscene.add_layer("world")

        def _add_branch(scene, key, parent):
            element = self.node_attribute(key, "element")

            frame = self.node_attribute(key, "frame")
            instance_of = self.node_attribute(key, "instance_of")
            scale = self.node_attribute(key, "scale")
            # TODO: auto attributes, but first key should not include "reference" key
            scene.add_layer(key, parent=parent, element=element, frame=frame, instance_of=instance_of, scale=scale)
            for child in self.nodes_where({"parent": key}):
                _add_branch(scene, child, key)

        _add_branch(subscene, key, world)
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

    # scene = Scene.from_gltf(gltf_filename)
    # print("GLTF")
    # print("=======================")
    # print(scene.data)

    scene_data_after = scene.data

    print(scene_data_before["node"])
    print(scene_data_after["node"])

    # assert scene_data_before["materials"] == scene_data_after["materials"]

    print(scene_data_before["materials"])
    print(scene_data_after["materials"])

    # assert scene_data_before["attributes"] == scene_data_after["attributes"]
    assert scene_data_before["dna"] == scene_data_after["dna"]
    assert scene_data_before["dea"] == scene_data_after["dea"]
    assert scene_data_before["adjacency"] == scene_data_after["adjacency"]
    assert scene_data_before["edge"] == scene_data_after["edge"]
