import os
import glob
from compas.datastructures import Mesh

from compas_xr import DATA
from compas_xr.datastructures import Scene

from compas.files.gltf.data_classes import MaterialData

scene = Scene.from_json(os.path.join(DATA, "idl.json"))
# 1. get root

materials_data = [{'name': 'Rhino Default', 'pbrMetallicRoughness': {'baseColorFactor': [1.0, 1.0, 1.0, 1.0], 'metallicFactor': 0.1, 'roughnessFactor': 0.5}, 'doubleSided': True},
                  {'name': '7021_Schwarzgrau_Nextel Dark Black', 'pbrMetallicRoughness': {'baseColorFactor': [0.1882353, 0.196078435, 0.203921571, 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.5}, 'doubleSided': True, 'extensions': {
                      'KHR_materials_pbrSpecularGlossiness': {'diffuseFactor': [0.1882353, 0.196078435, 0.203921571, 1.0], 'specularFactor': [0.0, 0.0, 0.0], 'glossinessFactor': 0.0}}},
                  {'name': '7036_Platingrau', 'pbrMetallicRoughness': {'baseColorFactor': [0.5921569, 0.5764706, 0.572549045, 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.5}, 'doubleSided': True, 'extensions': {
                      'KHR_materials_pbrSpecularGlossiness': {'diffuseFactor': [0.5921569, 0.5764706, 0.572549045, 1.0], 'specularFactor': [0.0, 0.0, 0.0], 'glossinessFactor': 0.0}}},
                  {'name': 'Cara_03 Shedland', 'pbrMetallicRoughness': {'baseColorFactor': [0.980392158, 0.980392158, 0.980392158, 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.5}, 'doubleSided': True, 'extensions': {
                      'KHR_materials_pbrSpecularGlossiness': {'diffuseFactor': [0.980392158, 0.980392158, 0.980392158, 1.0], 'specularFactor': [0.0, 0.0, 0.0], 'glossinessFactor': 0.0}}},
                  ]

#{'name': '7036_Platingrau', 'pbrMetallicRoughness': {'baseColorFactor': [0.5921569, 0.5764706, 0.572549045, 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.5}, 'doubleSided': True, 'extensions': {'KHR_materials_pbrSpecularGlossiness': {'diffuseFactor': [0.5921569, 0.5764706, 0.572549045, 1.0], 'specularFactor': [0.0, 0.0, 0.0], 'glossinessFactor': 0.0}}},
#{'name': 'Cara_03 Shedland', 'pbrMetallicRoughness': {'baseColorFactor': [0.980392158, 0.980392158, 0.980392158, 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.5}, 'doubleSided': True, 'extensions': {'KHR_materials_pbrSpecularGlossiness': {'diffuseFactor': [0.980392158, 0.980392158, 0.980392158, 1.0], 'diffuseTexture': {'index': 0, 'extensions': {'KHR_texture_transform': {'rotation': 0.0, 'scale': [70.0, 70.0]}}}, 'specularFactor': [0.0, 0.0, 0.0], 'glossinessFactor': 0.0}}},


scene.materials = [MaterialData.from_data(d) for d in materials_data]


"""
"extensionsUsed": [
    "KHR_materials_pbrSpecularGlossiness",
    "KHR_texture_transform",
    "KHR_draco_mesh_compression"
  ],
  "extensionsRequired": [
    "KHR_draco_mesh_compression"
  ],

"""


scene.to_gltf(os.path.join(DATA, "idl.gltf"))
scene.to_usd(os.path.join(DATA, "idl.usda"))
