import os
import pytest
from compas.geometry import Box
from compas.geometry import Frame, Rotation, Vector
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

BASE_FOLDER = os.path.dirname(__file__)


@pytest.fixture
def scene_with_material():
    scene = Scene()
    world = scene.add_layer("world")

    material = Material(name="material")
    material.pbr_metallic_roughness = PBRMetallicRoughness()
    material.pbr_metallic_roughness.base_color_factor = [0.9, 0.4, 0.2, 1.0]
    material.pbr_metallic_roughness.metallic_factor = 0.0
    material.pbr_metallic_roughness.roughness_factor = 0.5
    mkey = scene.add_material(material)

    rotation = Rotation.from_basis_vectors(Vector(0.936, 0.275, -0.218), Vector(-0.274, 0.961, 0.037))
    frame = Frame.from_rotation(rotation, point=[1, 2, 3])
    box = Box(frame, 1, 1, 1)
    scene.add_layer("box", parent=world, element=box, material=mkey)  # material_key=mkey
    return scene


@pytest.fixture
def scene_with_material_texture():
    scene = Scene()
    world = scene.add_layer("world")
    image_uri = "compas_icon_white.png"
    image_file = os.path.join(BASE_FOLDER, "fixtures", image_uri)
    image_data = Image(name=image_uri, mime_type=MineType.PNG, uri=image_file)
    # image_idx = scene.add_image(image_data)
    texture = Texture(source=image_data)
    # texture_idx = scene.add_texture(texture)

    # texture = Texture(source=texture)
    # texture_idx2 = scene.add_texture(texture)

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

    material_key = scene.add_material(material)  # TODO

    # add box
    box = Box(Frame.worldXY(), 1, 1, 1)
    mesh = Mesh.from_shape(box)
    mesh.quads_to_triangles()

    scene.add_layer("mesh", parent=world, element=box, material=material_key)
    return scene


@pytest.fixture
def scene_with_instances():
    pass


def test_gltf_export_import(scene_with_material):
    scene = scene_with_material
    scene_data_before = scene.data
    gltf_filename = os.path.join(DATA, "test_scene.gltf")
    scene.to_gltf(gltf_filename)
    scene = Scene.from_gltf(gltf_filename)
    scene_data_after = scene.data

    assert scene_data_before["materials"] == scene_data_after["materials"]
    assert scene_data_before["attributes"] == scene_data_after["attributes"]
    assert scene_data_before["dna"] == scene_data_after["dna"]
    assert scene_data_before["dea"] == scene_data_after["dea"]
    assert scene_data_before["adjacency"] == scene_data_after["adjacency"]
    assert scene_data_before["edge"] == scene_data_after["edge"]


def test_usd_export_import(scene_with_material):
    scene = scene_with_material
    scene_data_before = scene.data
    usd_filename = os.path.join(DATA, "test_scene.usda")
    scene.to_usd(usd_filename)
    scene = Scene.from_usd(usd_filename)
    scene_data_after = scene.data

    # assert scene_data_before["materials"] == scene_data_after["materials"] # TODO
    # assert scene_data_before["attributes"] == scene_data_after["attributes"] # TODO {'name': 'scene'} != {'name': 'usd_scene'}
    assert scene_data_before["dna"] == scene_data_after["dna"]
    assert scene_data_before["dea"] == scene_data_after["dea"]
    assert scene_data_before["adjacency"] == scene_data_after["adjacency"]
    assert scene_data_before["edge"] == scene_data_after["edge"]


def test_scene_data(scene_with_material_texture):
    scene = scene_with_material_texture
    data_before = scene.data
    scene = Scene.from_data(scene.data)
    data_after = scene.data
    assert data_before == data_after
