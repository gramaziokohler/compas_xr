import os
import pytest
from compas.geometry import Box
from compas.geometry import Frame, Rotation, Vector
from compas_xr import DATA
from compas_xr.datastructures import Scene
from compas_xr.datastructures import Material
from compas_xr.datastructures import PBRMetallicRoughness


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

    # assert scene_data_before["materials"] == scene_data_after["materials"]
    # assert scene_data_before["attributes"] == scene_data_after["attributes"]
    assert scene_data_before["dna"] == scene_data_after["dna"]
    assert scene_data_before["dea"] == scene_data_after["dea"]
    assert scene_data_before["adjacency"] == scene_data_after["adjacency"]
    assert scene_data_before["edge"] == scene_data_after["edge"]
