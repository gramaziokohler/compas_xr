import os
from compas.geometry import Box
from compas.geometry import Frame
from compas.datastructures import Mesh
from compas_xr.datastructures import Scene
from compas_xr.datastructures import Material
from compas_xr.datastructures import PBRMetallicRoughness
from compas_xr.datastructures.material import PBRSpecularGlossiness
from compas_xr.datastructures.material import Image
from compas_xr.datastructures.material import MineType
from compas_xr.datastructures.material import Texture
from compas_xr.datastructures.material import TextureInfo
from compas_xr.datastructures.material import TextureTransform

HERE = os.path.dirname(__file__)


scene = Scene()
world = scene.add_layer("world")
image_uri = "compas_icon_white.png"
image_file = os.path.join(HERE, image_uri)
image_data = Image(name=image_uri, mime_type=MineType.PNG, uri=image_file)
texture = Texture(source=image_data)

material = Material()
material.name = "Texture"
material.pbr_metallic_roughness = PBRMetallicRoughness()
material.pbr_metallic_roughness.metallic_factor = 0.0
material.pbr_metallic_roughness.base_color_texture = TextureInfo(texture=texture)

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

scene.add_layer("mesh", parent=world, element=mesh, material=material_key)

filename = os.path.join(HERE, "scene_with_texture.gltf")
scene.to_gltf(filename)
print(filename)
