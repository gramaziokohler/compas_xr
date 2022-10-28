from compas.files.gltf.data_classes import MaterialData

from compas.files.gltf.extensions import KHR_materials_pbrSpecularGlossiness
from compas.files.gltf.extensions import KHR_materials_clearcoat
from compas.files.gltf.extensions import KHR_materials_transmission
from compas.files.gltf.extensions import KHR_materials_specular
from compas.files.gltf.extensions import KHR_materials_ior

replace_map = {
    "pbr_metallic_roughness": "pbrMetallicRoughness",
    "normal_texture": "normalTexture",
    "occlusion_texture": "occlusionTexture",
    "emissive_texture": "emissiveTexture",
    "emissive_factor": "emissiveFactor",
    "alpha_mode": "alphaMode",
    "alpha_cutoff": "alphaCutoff",
    "double_sided": "doubleSided",
    "base_color_factor": "baseColorFactor",
    "base_color_texture": "baseColorTexture",
    "metallic_factor": "metallicFactor",
    "roughness_factor": "roughnessFactor",
    "metallic_roughness_texture": "metallicRoughnessTexture",
    "diffuse_factor": "diffuseFactor",
    "diffuse_texture": "diffuseTexture",
    "specular_factor": "specularFactor",
    "glossiness_factor": "glossinessFactor",
    "specular_glossiness_texture": "specularGlossinessTexture",
    "clearcoat_factor": "clearcoatFactor",
    "clearcoat_texture": "clearcoatTexture",
    "clearcoat_roughness_factor": "clearcoatRoughnessFactor",
    "clearcoat_roughness_texture": "clearcoatRoughnessTexture",
    "clearcoat_normal_texture": "clearcoatNormalTexture",
    "transmission_factor": "transmissionFactor",
    "transmission_texture": "transmissionTexture",
    "specular_factor": "specularFactor",
    "specular_texture": "specularTexture",
    "specular_color_factor": "specularColorFactor",
    "specular_color_texture": "specularColorTexture",
}
replace_map_inv = {v: k for k, v in replace_map.items()}


def replace_recursively(adict, replace_map, ndict=None):
    if ndict is None:
        ndict = {}
    for k, v in adict.items():
        nk = replace_map[k] if k in replace_map else k
        if isinstance(v, dict):
            if k not in ndict:
                ndict[nk] = {}
            replace_recursively(v, replace_map, ndict[nk])
        else:
            ndict[nk] = v
    return ndict


class GLTFMaterial(MaterialData):  # TODO: base on BaseMaterial?
    def __init__(self, *args, **kwargs):
        super(GLTFMaterial, self).__init__(*args, **kwargs)
        self.content = None

    @classmethod
    def from_material(cls, content, material):
        material_dict = replace_recursively(material.data, replace_map)
        obj = super(GLTFMaterial, cls).from_data(material_dict)

        # extensions
        if "pbr_specular_glossiness" in material_dict and material_dict["pbr_specular_glossiness"] is not None:
            ext = KHR_materials_pbrSpecularGlossiness.from_data(material_dict["pbr_specular_glossiness"])
            obj.add_extension(ext)
        if "transmission" in material_dict and material_dict["transmission"] is not None:
            ext = KHR_materials_transmission.from_data(material_dict["transmission"])
            obj.add_extension(ext)
        if "clearcoat" in material_dict and material_dict["clearcoat"] is not None:
            ext = KHR_materials_clearcoat.from_data(material_dict["clearcoat"])
            obj.add_extension(ext)
        if "ior" in material_dict and material_dict["ior"] is not None:
            ext = KHR_materials_ior.from_data(material_dict["ior"])
            obj.add_extension(ext)
        if "specular" in material_dict and material_dict["specular"] is not None:
            ext = KHR_materials_specular.from_data(material_dict["specular"])
            obj.add_extension(ext)

        obj.content = content
        return obj

    @classmethod
    def from_material_data(cls, content, material_data):
        texture_index_by_key = 0  # TODO
        obj = super(GLTFMaterial, cls).from_data(material_data.to_data(texture_index_by_key))
        obj.content = content  # TODO check why this is needed
        return obj

    def to_compas(self):
        from compas_xr.datastructures import Material

        texture_index_by_key = 0  # TODO
        # TODO: extensions
        material_dict = replace_recursively(self.to_data(texture_index_by_key), replace_map_inv)
        return Material.from_data(material_dict)
