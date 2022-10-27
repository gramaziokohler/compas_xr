import os
import glob
from compas.datastructures import Mesh

from compas_xr import DATA
from compas_xr.datastructures import Scene, Material
from compas_xr.datastructures.material import PBRMetallicRoughness
from compas_xr.datastructures.material import PBRSpecularGlossiness


HERE = os.path.dirname(__file__)

scene = Scene.from_json(os.path.join(HERE, "idl.json"))


material = Material()
material.name = "Rhino_Default"
material.pbr_metallic_roughness = PBRMetallicRoughness()
material.pbr_metallic_roughness.metallic_factor = 0.1
material.pbr_metallic_roughness.roughness_factor = 0.5
material.pbr_metallic_roughness.base_color_factor = [1.0, 1.0, 1.0, 1.0]
material.double_sided = True
scene.add_material(material)


material = Material()
material.name = "Schwarzgrau_Nextel_Dark_Black"
material.pbr_metallic_roughness = PBRMetallicRoughness()
material.pbr_metallic_roughness.metallic_factor = 0.0
material.pbr_metallic_roughness.roughness_factor = 0.5
material.pbr_metallic_roughness.base_color_factor = [0.1882353, 0.196078435, 0.203921571, 1.0]
material.double_sided = True
# add extension
material.pbr_specular_glossiness = PBRSpecularGlossiness()
material.pbr_specular_glossiness.diffuse_factor = [0.1882353, 0.196078435, 0.203921571, 1.0]
material.pbr_specular_glossiness.specular_factor = [0.0, 0.0, 0.0]
material.pbr_specular_glossiness.glossiness_factor = 0.0
scene.add_material(material)

material = Material()
material.name = "Platingrau"
material.pbr_metallic_roughness = PBRMetallicRoughness()
material.pbr_metallic_roughness.metallic_factor = 0.0
material.pbr_metallic_roughness.roughness_factor = 0.5
material.pbr_metallic_roughness.base_color_factor = [0.5921569, 0.5764706, 0.572549045, 1.0]
material.double_sided = True
# add extension
material.pbr_specular_glossiness = PBRSpecularGlossiness()
material.pbr_specular_glossiness.diffuse_factor = [0.5921569, 0.5764706, 0.572549045, 1.0]
material.pbr_specular_glossiness.specular_factor = [0.0, 0.0, 0.0]
material.pbr_specular_glossiness.glossiness_factor = 0.0
scene.add_material(material)

material = Material()
material.name = "Cara_03_Shedland"
material.pbr_metallic_roughness = PBRMetallicRoughness()
material.pbr_metallic_roughness.metallic_factor = 0.0
material.pbr_metallic_roughness.roughness_factor = 0.5
material.pbr_metallic_roughness.base_color_factor = [0.980392158, 0.980392158, 0.980392158, 1.0]
material.double_sided = True
# add extension
material.pbr_specular_glossiness = PBRSpecularGlossiness()
material.pbr_specular_glossiness.diffuse_factor = [0.980392158, 0.980392158, 0.980392158, 1.0]
material.pbr_specular_glossiness.specular_factor = [0.0, 0.0, 0.0]
material.pbr_specular_glossiness.glossiness_factor = 0.0
scene.add_material(material)


ceiling_node = scene.add_node(key="ceiling", parent=None)
projection_node = scene.add_node(key="projection", parent="ceiling")
canvas_node = scene.add_node(key="canvas", parent="projection")

folder = os.path.join(HERE, "idl", "ceiling", "projection", "canvas")

for file in glob.glob("%s/*.obj" % folder):
    mesh = Mesh.from_obj(file)
    node_name = os.path.splitext(os.path.basename(file))[0]
    key = scene.add_node(key=node_name, element=mesh, parent="canvas")

scene.to_gltf(os.path.join(HERE, "canvas.gltf"))
scene.to_usd(os.path.join(HERE, "canvas.usda"))


"""
# Animation

animated_node = get_node_by_name(content, "leinwand")

channels = []
channels.append(ChannelData(0, TargetData("scale", node=animated_node.key)))
channels.append(ChannelData(1, TargetData("translation", node=animated_node.key)))

# R0=(1,0,0,0), R1=(0,1,0,0), R2=(0,0,49.3,-243.8667), R3=(0,0,0,1)

samplers_dict = {}
# scale
input = [0.0, 5.0]
output = [(1.0, 1.0, 1.0), (1.0, 1.0, 49.3)]
interpolation = "LINEAR"
samplers_dict[0] = AnimationSamplerData(input, output, interpolation)
# translation
input = [0.0, 5.0]
output = [(0.0, 0.0, 0.0), (0.0, 0.0, -243.8667)]
interpolation = "LINEAR"
samplers_dict[1] = AnimationSamplerData(input, output, interpolation)

animation = AnimationData(channels, samplers_dict, name="anim1")
content.animations = {0: animation}
exporter = GLTFExporter(filepath, content, embed_data=True)
exporter.export()
"""
