import os

import compas

from compas.geometry import Box, Frame
from compas.datastructures import Mesh

from compas_xr import DATA
from compas_xr.datastructures import Scene
from compas_xr.datastructures import Material
from compas_xr.datastructures import PBRMetallicRoughness
from compas_xr.datastructures.material import PBRSpecularGlossiness
from compas_xr.datastructures.material import Image
from compas_xr.datastructures.material import MineType
from compas_xr.datastructures.material import Texture
from compas_xr.datastructures.material import TextureInfo
from compas_xr.datastructures.material import TextureTransform


def test_material():

    gltf_filepath = os.path.join(DATA, "mesh_with_material.gltf")
    glb_filepath = os.path.join(DATA, "mesh_with_material.glb")
    usd_filepath = os.path.join(DATA, "mesh_with_material.usda")

    color = (1.0, 0.4, 0)
    material = Material()
    material.name = "Plaster"
    material.double_sided = True
    material.pbr_metallic_roughness = PBRMetallicRoughness()
    material.pbr_metallic_roughness.base_color_factor = list(color) + [1.0]  # [0, 1, 0, 1.0]
    material.pbr_metallic_roughness.metallic_factor = 0.0
    material.pbr_metallic_roughness.roughness_factor = 0.5

    scene = Scene()
    world = scene.add_layer("world")
    mkey = scene.add_material(material)
    cmesh = Mesh.from_polyhedron(8)
    scene.add_layer("element", parent=world, element=cmesh, material=mkey)

    scene.to_gltf(gltf_filepath)
    scene.to_gltf(glb_filepath, embed_data=True)
    scene.to_usd(usd_filepath)


def test_material2():

    scene = Scene()
    world = scene.add_layer("world")

    dirname = os.path.join(compas.APPDATA, "data", "gltfs")

    image_uri = "compas_icon_white.png"
    image_file = os.path.join(dirname, image_uri)
    image_data = Image(name=image_uri, mime_type=MineType.PNG, uri=image_file)

    texture = Texture(source=image_data)

    material = Material()
    material.name = "Texture"
    material.pbr_metallic_roughness = PBRMetallicRoughness()
    material.pbr_metallic_roughness.metallic_factor = 0.0
    material.pbr_metallic_roughness.base_color_texture = TextureInfo(texture=texture)

    # add extension
    material.pbr_specular_glossiness = PBRSpecularGlossiness()
    material.pbr_specular_glossiness.diffuse_factor = [0.98, 0.98, 0.98, 1.0]
    material.pbr_specular_glossiness.specular_factor = [0.0, 0.0, 0.0]
    material.pbr_specular_glossiness.glossiness_factor = 0.0
    texture_transform = TextureTransform(rotation=0.0, scale=[2.0, 2.0])

    material.pbr_specular_glossiness.diffuse_texture = TextureInfo(texture=texture)
    material.pbr_specular_glossiness.diffuse_texture.texture_transform = texture_transform

    material_key = scene.add_material(material)

    # add box
    box = Box(Frame.worldXY(), 1, 1, 1)
    mesh = Mesh.from_shape(box)
    mesh.quads_to_triangles()

    normals = [mesh.vertex_normal(k) for k in mesh.vertices()]
    texture_coordinates = [
        (0.0, 1.0),
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]

    for k, v in zip(mesh.vertices(), texture_coordinates):
        mesh.vertex_attribute(k, "texture_coordinate", value=v)

    node = scene.add_layer("mesh", parent=world, element=mesh, material=material_key)  # why material key???

    data_before = scene.data

    scene = Scene.from_data(scene.data)

    data_after = scene.data

    assert data_before == data_after

    """
    for k, v in data_before.items():
        print(k)
        if k == "materials":
            for i, m in enumerate(data_before[k]):
                for l, m in data_before[k][i].items():
                    print(l)
                    print(data_before[k][i][l])
                    print(data_after[k][i][l])
                    print()
        else:
            print(data_before[k])
            print(data_after[k])

        print()
    """

    """
    pd = node.mesh_data.primitive_data_list[0]
    pd.material = material_key
    pd.attributes["TEXCOORD_0"] = texcoord_0
    pd.attributes["NORMAL"] = normals
    """
