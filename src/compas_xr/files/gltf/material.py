from compas.files.gltf.data_classes import MaterialData

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


class GLTFMaterial(MaterialData):
    def __init__(self, *args, **kwargs):
        super(GLTFMaterial, self).__init__(*args, **kwargs)
        self.content = None

    @classmethod
    def from_material(cls, content, material):
        material_dict = replace_recursively(material.data, replace_map)
        obj = super(GLTFMaterial, cls).from_data(material_dict)
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
