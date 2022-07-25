from compas.files import GLTF
from compas.files import GLTFContent
from compas.files import GLTFExporter

from compas.datastructures import Mesh
from compas.geometry import Rotation

from compas_xr.files.gltf import GLTFMaterial


class GLTFScene(object):
    """ """

    def __init__(self, content=None):
        self.content = content

    @classmethod
    def from_gltf(cls, filename):
        gltf = GLTF(filename)
        gltf.read()
        return cls(content=gltf.content)

    @classmethod
    def from_scene(cls, scene):

        gltf_scene = cls(content=GLTFContent())
        content = gltf_scene.content
        gscene = content.add_scene(scene.name)

        for material in scene.materials:
            gltf_material = GLTFMaterial.from_material(content, material)
            content.add_material(gltf_material)

        # Add those that are references first
        visited = []
        for key in scene.nodes_where({"is_reference": True}):
            shortest_path = scene.node_to_root(key)
            for key in reversed(shortest_path):
                if key not in visited:
                    gltf_scene.add_gltf_node_to_content(scene, gscene, key)
                    visited.append(key)

        for key in scene.ordered_keys:
            if key not in visited:
                gltf_scene.add_gltf_node_to_content(scene, gscene, key)

        return gltf_scene

    def add_gltf_node_to_content(self, graph, scene, key):
        # graph, = self
        parent = graph.node_attribute(key, "parent")
        is_reference = graph.node_attribute(key, "is_reference")
        frame = graph.node_attribute(key, "frame")
        element = graph.node_attribute(key, "element")
        instance_of = graph.node_attribute(key, "instance_of")
        material = graph.node_attribute(key, "material")

        if not parent:
            node = self.content.add_node_to_scene(scene, node_name=key)
        else:
            parent = self.content.get_node_by_name(parent)

            node = self.content.add_child_to_node(parent, key)

        if frame:  # TODO scale
            node.translation = list(frame.point)
            node.rotation = list(Rotation.from_frame(frame).quaternion.xyzw)

        if instance_of:
            reference = self.content.get_node_by_name(instance_of)
            node.mesh_key = reference.mesh_key
        elif is_reference:
            # set invisible?
            pass

        if element:
            mesh = Mesh.from_shape(element)  # if shape, else take Mesh directly
            mesh.quads_to_triangles()
            self.content.add_mesh_to_node(node, mesh)

        if material is not None:  # == key
            node.mesh_data.primitive_data_list[0].material = material

    def to_compas(self):
        # returns a :class:`Scene` object

        from compas_xr.datastructures import Scene

        content = self.content
        if len(content.scenes) > 1:
            raise ValueError("More than one scene per content is currently not supported")

        for key, scene in content.scenes.items():
            scene = Scene(name=scene.name, up_axis="Z")

        for mkey, mdata in content.materials.items():

            gmat = GLTFMaterial.from_material_data(content, mdata)
            material = gmat.to_compas()

    def to_gltf(self, filename, embed_data=False):
        exporter = GLTFExporter(filename, self.content, embed_data=embed_data)
        exporter.export()


if __name__ == "__main__":
    import os
    from compas_xr import DATA

    filepath = os.path.join(DATA)
