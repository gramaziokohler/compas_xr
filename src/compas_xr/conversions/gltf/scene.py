from compas.files import GLTF
from compas.files import GLTFContent
from compas.files import GLTFExporter

from compas.datastructures import Mesh
from compas.geometry import Rotation
from compas.geometry import Frame

from compas_xr.conversions import BaseScene


from .material import GLTFMaterial


class GLTFScene(BaseScene):
    """Scene to handle GLTF coversion"""

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

        from compas.files.gltf.data_classes import ImageData
        from compas.files.gltf.data_classes import TextureData

        for image in scene.images:
            image_data = ImageData(name=image.name, mime_type=image.mime_type, uri=image.uri)
            content.add_image(image_data)

        for texture in scene.textures:
            texture = TextureData(source=texture.index, name=texture.name)  # 'offset': [0.0, 0.0], 'rotation': 0.0, 'repeat': [0, 0], 'scale': [1.0, 1.0]}
            content.add_texture(texture)

        for material in scene.materials:
            gltf_material = GLTFMaterial.from_material(content, material)
            content.add_material(gltf_material)

        # Go through references and add those with the deepest depth first
        visited = []
        for key in scene.ordered_references:
            shortest_path = scene.node_to_root(key)
            for key in reversed(shortest_path):
                gltf_scene._add_gltf_node_to_content(scene, gscene, key)
            children = scene._all_children(key, include_key=True)
            visited += children

        for key in scene.ordered_keys:
            if key not in visited:
                gltf_scene._add_gltf_node_to_content(scene, gscene, key)

        return gltf_scene

    def _add_gltf_node_to_content(self, graph, scene, key):
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
            # here we need to copy the whole tree of the instance
            node.mesh_key = reference.mesh_key
            for child in graph._all_children(instance_of, include_key=False):
                new_name = "%s_%s" % (node.name, child)
                child_node = self.content.get_node_by_name(child)
                if child_node.mesh_key:
                    new_child_node = self.content.add_child_to_node(node, new_name)
                    new_child_node.mesh_key = child_node.mesh_key

        elif is_reference:
            # set invisible?
            # iter through children
            children = graph._all_children(key, include_key=False)
            for child in children:
                self._add_gltf_node_to_content(graph, scene, child)

        if element:
            mesh = element if type(element) == Mesh else Mesh.from_shape(element)
            mesh.quads_to_triangles()
            self.content.add_mesh_to_node(node, mesh)

        if material is not None:  # == key
            if node.mesh_data:
                for pd in node.mesh_data.primitive_data_list:
                    pd.material = material

    def to_compas(self):
        # returns a :class:`Scene` object

        from compas_xr.datastructures import Scene

        content = self.content
        if len(content.scenes) > 1:
            raise ValueError("More than one scene per content is currently not supported")

        for _, scene in content.scenes.items():
            scene = Scene(name=scene.name, up_axis="Z")

        # add materials
        for _, mdata in content.materials.items():
            gmat = GLTFMaterial.from_material_data(content, mdata)
            material = gmat.to_compas()
            _ = scene.add_material(material)  # does the key get mixed up?

        # iter through nodes, add geometry
        names, parents, frames, elements, materials = {}, {}, {}, {}, {}

        for key, node in content.nodes.items():
            names[key] = node.name
            for child in node.children:
                parents[child] = node.name

            T = None
            # if node.translation:
            #    print("node.translation", node.translation)
            # if node.rotation:
            #    print("node.rotation", node.rotation)
            #    # node.rotation = list(Rotation.from_frame(frame).quaternion.xyzw)
            if T:
                frames[key] = Frame.from_transformation(T)

            if node.mesh_key is not None:
                gltf_mesh = content.meshes[node.mesh_key]  # this won't check if already used.. so instances are not supported
                mesh = Mesh.from_vertices_and_faces(gltf_mesh.vertices, gltf_mesh.faces)
                elements[key] = mesh

                for pd in gltf_mesh.primitive_data_list:
                    if pd.material is not None:
                        materials[key] = pd.material  # does the key get mixed up?

        for key in content.nodes:
            name = names.get(key, None)
            parent = parents.get(key, None)
            material = materials.get(key, None)
            element = elements.get(key, None)
            frame = frames.get(key, None)
            # is_reference ?
            # instance_of ?
            print(name, parent, frame, element, material)
            scene.add_layer(name, parent=parent, frame=frame, element=element, material=material)

        return scene

    def to_gltf(self, filename, embed_data=False):
        exporter = GLTFExporter(filename, self.content, embed_data=embed_data)
        exporter.export()
