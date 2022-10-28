from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas
from compas.topology import breadth_first_ordering
from compas.datastructures import Graph

if not compas.IPY:
    from compas_xr.conversions.usd import USDScene
from compas_xr.conversions.gltf import GLTFScene

from .material import Image
from .material import Texture
from .material import Material
from .material import TextureInfo
from compas.data import Data

__all__ = ["Scene"]


def argsort(seq):  # TODO: upstream to compas
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)


class Scene(Graph):
    """Scene data structure for describing a scene composed by layers and elements (geometry), materials, animations, lights, cameras, etc.

    Parameters
    ----------
    name : str, optional
        The name of the datastructure. Defaults to "scene".
    up_axis : str, optional
        The axis that looks up. Defaults to "Z"
    materials : list of :class:`compas_xr.datastructures.Material`, optional
        The materials of the scene


    Attributes
    ----------
    images : list of :class:`compas_xr.datastructures.Image`
        The images contained in the materials of the scene.
    textures : list of :class:`compas_xr.datastructures.Texture`
        The textures contained in the materials of the scene.
    """

    def __init__(self, name="scene", up_axis="Z", materials=None):
        super(Scene, self).__init__()
        self.name = name
        self.up_axis = up_axis
        self.materials = materials or []
        self._images = []
        self._textures = []
        self.update_default_node_attributes({"is_reference": False})

    def add_layer(self, layer_name, parent=None, attr_dict=None, **kwattr):
        """Adds a layer to the scene.

        Parameters
        ----------
        layer_name : str
            The name of the layer
        parent : str, optional
            The name of the parent

        Returns
        -------
        str
            The name of the added layer.
        """
        self.add_node(layer_name, parent=parent, attr_dict=attr_dict, **kwattr)
        if parent:
            if self.has_layer(parent):
                self.add_edge(parent, layer_name)
            else:
                raise ValueError("Parent %s does not exist in scene." % parent)
        return layer_name

    def add_material(self, material):
        """Adds a material to the scene."""
        self.materials.append(material)
        self._replace_image_and_texture_indices_recursively(material)
        return len(self.materials) - 1

    # --------------------------------------------------------------------------
    # helpers
    # --------------------------------------------------------------------------

    def has_layer(self, layer_name):
        """Returns `True` if the layer exists, `False` otherwise."""
        return self.has_node(layer_name)

    def unique_key(self, name, num_padding=3, i=0):
        """Returns a unique key in the scene.

        Parameters
        ----------
        name : str
            The name of the layer
        num_padding : int, optional
            The padding of the counter, defaults to 3.
        i : int, optional
            The number of starting counting, defaults to 0.

        Returns
        -------
        str
            The name of a unique key.

        """
        if not self.has_node(name):
            return name
        postfix = "%0" + str(num_padding) + "d"
        key = (name + postfix) % (i)
        while self.has_node(key):
            i += 1
            key = (name + postfix) % (i)
        return key

    def material_index_by_name(self, name):
        for i, m in enumerate(self.materials):
            if m.name == name:
                return i
        return None

    # --------------------------------------------------------------------------
    # properties
    # --------------------------------------------------------------------------

    @property
    def textures(self):
        return self._textures

    @property
    def images(self):
        return self._images

    @property
    def material_names(self):  # TODO: check if this is used at all
        for material in self.materials:
            yield material.name

    @property
    def ordered_keys(self):
        for root in self.nodes_where({"parent": None}):
            for key in breadth_first_ordering(self.adjacency, root):
                yield key

    def node_to_root(self, key):  # TODO: check if this is used at all
        shortest_path = [key]
        parent = self.node_attribute(key, "parent")
        while parent:
            shortest_path.append(parent)
            key = parent
            parent = self.node_attribute(key, "parent")
        return shortest_path

    @property
    def has_references(self):
        """Returns `True` if the scene contains references, `False` otherwise."""
        references = list(self.nodes_where({"is_reference": True}))
        return bool(len(references))

    @property
    def ordered_references(self):
        """Returns an ordered list of references, starting with the deepest depth first."""
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

    def _replace_image_and_texture_indices_recursively(self, item):
        # todo go deep into material and check if we need to add texture etc and replace
        for a in dir(item):
            if (
                not a.startswith("__")
                and a
                not in [
                    "DATASCHEMA",
                    "_JSONSCHEMA",
                    "JSONSCHEMA",
                    "JSONSCHEMANAME",
                    "guid",
                    "jsondefinitions",
                    "jsonstring",
                    "jsonvalidator",
                    "_guid",
                    "_jsondefinitions",
                    "_jsonvalidator",
                    "data",
                    "_name",
                    "dtype",
                ]
                and not callable(getattr(item, a))
            ):  # TODO: better?

                attr = getattr(item, a)
                if isinstance(attr, TextureInfo):
                    if attr.texture is not None:
                        texture = attr.texture
                        image = texture.source
                        if image:
                            if image not in self._images:
                                self._images.append(image)
                                image_idx = len(self._images) - 1
                            else:
                                image_idx = self._images.index(image)
                            texture.index = image_idx

                        if texture not in self._textures:
                            self._textures.append(texture)
                            texture_idx = len(self._textures) - 1
                        else:
                            texture_idx = self._textures.index(texture)
                        attr.index = texture_idx

                elif isinstance(attr, Data):
                    self._replace_image_and_texture_indices_recursively(attr)

    # --------------------------------------------------------------------------
    # data
    # --------------------------------------------------------------------------

    @property
    def data(self):
        # for material in self.materials:
        #    self._replace_image_and_texture_indices_recursively(material)
        data = super(Scene, self).data
        if self._images is not None:
            data["images"] = [m.data for m in self._images]
        if self._textures is not None:
            data["textures"] = [m.data for m in self._textures]
        if self.materials is not None:
            data["materials"] = [m.data for m in self.materials]
        return data

    @data.setter
    def data(self, data):
        super(Scene, self.__class__).data.fset(self, data)
        if data.get("images") is not None:
            self._images = [Image.from_data(d) for d in data.get("images")]
        if data.get("textures") is not None:
            self._textures = [Texture.from_data(d) for d in data.get("textures")]
            for t in self._textures:
                if t.index is not None:
                    t.source = self._images[t.index]  # link them
                else:
                    raise Exception("ss")
        if data.get("materials") is not None:
            self.materials = [Material.from_data(d) for d in data.get("materials")]

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_gltf(cls, filepath):
        return GLTFScene.from_gltf(filepath).to_compas()

    @classmethod
    def from_usd(cls, filepath):
        return USDScene.from_usd(filepath).to_compas()

    def to_usd(self, filepath):
        USDScene.from_scene(self).to_usd(filepath)

    def to_gltf(self, filepath, embed_data=False):
        GLTFScene.from_scene(self).to_gltf(filepath, embed_data=embed_data)

    def subscene(self, key):
        """Creates a sub scene with key as root layer."""
        subscene = Scene()
        world = subscene.add_layer("world")

        # self._images = images or [] TODO
        # self._textures = textures or [] TODO

        def _add_branch(scene, key, parent):

            print(">>>>", self.node_attributes(key))
            element = self.node_attribute(key, "element")
            is_reference = self.node_attribute(key, "is_reference")
            frame = self.node_attribute(key, "frame")
            instance_of = self.node_attribute(key, "instance_of")
            scale = self.node_attribute(key, "scale")

            tex_coords = self.node_attribute(key, "tex_coords")
            mkey = self.node_attribute(key, "material")
            if mkey is not None:
                material = self.materials[mkey]
                mkey = scene.add_material(material)

            # TODO: auto copy attributes !!!
            scene.add_layer(key, parent=parent, element=element, frame=frame, instance_of=instance_of, scale=scale, is_reference=is_reference, tex_coords=tex_coords, material=mkey)
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
