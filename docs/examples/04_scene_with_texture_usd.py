import os

from compas.datastructures import Mesh
from compas_xr.datastructures import PBRMetallicRoughness
from compas_xr.datastructures import Scene, Material
from compas_xr.datastructures.material import PBRSpecularGlossiness
from compas_xr.datastructures.material import MineType
from compas_xr.datastructures.material import Texture
from compas_xr.datastructures.material import TextureInfo
from compas_xr.datastructures.material import Image

from compas_xr.conversions.usd import USDScene

HERE = os.path.dirname(__file__)


scene = Scene(up_axis="Y")
root = scene.add_layer("TexModel")
material = Material(name="boardMat")

# attach surface shader
material.pbr_metallic_roughness = PBRMetallicRoughness()
material.pbr_metallic_roughness.metallic_factor = 0.0
material.pbr_metallic_roughness.roughness_factor = 0.4

# attach texture
image_uri = "USDLogoLrg.png"
image_file = os.path.join(HERE, image_uri)
image_data = Image(name=image_uri, mime_type=MineType.PNG, uri=image_file)
texture = Texture(source=image_data, name="UsdUVTexture")
material.pbr_specular_glossiness = PBRSpecularGlossiness()
material.pbr_specular_glossiness.diffuse_texture = TextureInfo(texture=texture)

mkey = scene.add_material(material)

# attach billboard
vertices = [(-430, -145, 0), (430, -145, 0), (430, 145, 0), (-430, 145, 0)]
faces = [[0, 1, 2, 3]]
billboard = Mesh.from_vertices_and_faces(vertices, faces)
texture_coordinates = [(0, 0), (1, 0), (1, 1), (0, 1)]
for k, v in zip(billboard.vertices(), texture_coordinates):
    billboard.vertex_attribute(k, "texture_coordinate", value=v)
scene.add_layer("card", parent=root, element=billboard, material=mkey)

filename = os.path.join(HERE, "test2.usda")
USDScene.from_scene(scene).to_usd(filename)
