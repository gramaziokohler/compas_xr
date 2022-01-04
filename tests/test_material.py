import os
from compas.datastructures import Mesh
from compas_xr.datastructures import Material
from compas_xr.datastructures.material import PBRMetallicRoughness
from compas_xr.datastructures import Scene
from compas_xr import DATA

def test_material():
    
    gltf_filepath = os.path.join(DATA, "mesh_with_material.gltf")
    glb_filepath = os.path.join(DATA, "mesh_with_material.glb")
    usd_filepath = os.path.join(DATA, "mesh_with_material.usda")

    color = (1., 0.4, 0)
    material = Material()
    material.name = 'Plaster'
    material.double_sided = True
    material.pbr_metallic_roughness = PBRMetallicRoughness()
    material.pbr_metallic_roughness.base_color_factor = list(color) + [1.]  # [0, 1, 0, 1.0]
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