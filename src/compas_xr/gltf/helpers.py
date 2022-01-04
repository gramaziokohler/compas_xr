from compas.datastructures import Mesh
from compas.geometry import Rotation

# TODO: upstream to GLTF


class AlphaMode(object):
    BLEND = 'BLEND'
    MASK = 'MASK'
    OPAQUE = 'OPAQUE'


def mesh_add_material(mesh_data, material_key):  # needed?
    # TODO: GLTFMesh.add_material
    mesh_data.primitive_data_list[0].material = material_key


def gltf_get_node_by_name(content, name):
    for key in content.nodes:
        if content.nodes[key].name == name:
            return content.nodes[key]
    return None


def gltf_add_node_to_content(graph, content, scene, key):
    parent = graph.node_attribute(key, 'parent')
    is_reference = graph.node_attribute(key, 'is_reference')
    frame = graph.node_attribute(key, 'frame')
    element = graph.node_attribute(key, 'element')
    instance_of = graph.node_attribute(key, 'instance_of')
    material = graph.node_attribute(key, 'material')

    if not parent:
        node = content.add_node_to_scene(scene, node_name=key)
    else:
        parent = gltf_get_node_by_name(content, parent)
        node = content.add_child_to_node(parent, key)

    if frame:
        node.translation = list(frame.point)
        node.rotation = list(Rotation.from_frame(frame).quaternion.xyzw)

    if instance_of:
        reference = gltf_get_node_by_name(content, instance_of)
        node.mesh_key = reference.mesh_key
    elif is_reference:
        # set invisible?
        pass

    if element:
        mesh = Mesh.from_shape(element)  # if shape, else take Mesh directly
        mesh.quads_to_triangles()
        content.add_mesh_to_node(node, mesh)

    if material is not None:  # == key
        # key = gltf_material_index_by_name(content, material)
        node.mesh_data.primitive_data_list[0].material = material


def gltf_add_image_to_content():
    pass


def gltf_add_material_to_content(content, material):
    # TODO: content.add_material(material)
    key = len(content.materials)
    while key in content.materials:
        key += 1
    content.materials[key] = material
    return key


def gltf_material_index_by_name(content, name):  # needed?
    for key in content.materials:
        if content.materials[key].name == name:
            return key
    return None
