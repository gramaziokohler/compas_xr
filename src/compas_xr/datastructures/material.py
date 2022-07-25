from compas.data import Data

# https://github.com/KhronosGroup/glTF/blob/master/specification/2.0/schema/material.schema.json


class Material(Data):
    """ """

    def __init__(
        self,
        name=None,
        extras=None,
        pbr_metallic_roughness=None,
        normal_texture=None,
        occlusion_texture=None,
        emissive_texture=None,
        emissive_factor=None,
        alpha_mode=None,
        alpha_cutoff=None,
        double_sided=True,
    ):
        self.name = name
        self.extras = extras
        self.pbr_metallic_roughness = pbr_metallic_roughness
        self.normal_texture = normal_texture
        self.occlusion_texture = occlusion_texture
        self.emissive_texture = emissive_texture
        self.emissive_factor = emissive_factor
        self.alpha_mode = alpha_mode
        self.alpha_cutoff = alpha_cutoff
        self.double_sided = double_sided

    @property
    def data(self):
        return {
            "name": self.name,
            "extras": self.extras,
            "pbr_metallic_roughness": self.pbr_metallic_roughness.data if self.pbr_metallic_roughness else None,  # noqa E501
            "normal_texture": self.normal_texture.data if self.normal_texture else None,  # noqa E501
            "occlusion_texture": self.occlusion_texture.data if self.occlusion_texture else None,  # noqa E501
            "emissive_texture": self.emissive_texture.data if self.emissive_texture else None,  # noqa E501
            "emissive_factor": self.emissive_factor,
            "alpha_mode": self.alpha_mode,
            "alpha_cutoff": self.alpha_cutoff,
            "double_sided": self.double_sided,
        }

    @data.setter
    def data(self, data):
        self.name = data.get("name")
        self.extras = data.get("extras")
        self.pbr_metallic_roughness = PBRMetallicRoughness.from_data(data.get("pbr_metallic_roughness")) if data.get("pbr_metallic_roughness") else None  # noqa E501
        self.normal_texture = NormalTexture.from_data(data.get("normal_texture")) if data.get("normal_texture") else None  # noqa E501
        self.occlusion_texture = OcclusionTexture.from_data(data.get("occlusion_texture")) if data.get("occlusion_texture") else None  # noqa E501
        self.emissive_texture = Texture.from_data(data.get("emissive_texture")) if data.get("emissive_texture") else None  # noqa E501
        self.emissive_factor = data.get("emissive_factor")
        self.alpha_mode = data.get("alpha_mode")
        self.alpha_cutoff = data.get("alpha_cutoff")
        self.double_sided = data.get("double_sided")


class PBRMetallicRoughness(Data):
    def __init__(
        self,
        base_color_factor=None,
        base_color_texture=None,
        metallic_factor=None,
        roughness_factor=None,
        metallic_roughness_texture=None,
    ):
        self.base_color_factor = base_color_factor
        self.base_color_texture = base_color_texture
        self.metallic_factor = metallic_factor
        self.roughness_factor = roughness_factor
        self.metallic_roughness_texture = metallic_roughness_texture

    @property
    def data(self):
        return {
            "base_color_factor": self.base_color_factor,
            "base_color_texture": self.base_color_texture.data if self.base_color_texture else None,  # noqa E501
            "metallic_factor": self.metallic_factor,
            "roughness_factor": self.roughness_factor,
            "metallic_roughness_texture": self.metallic_roughness_texture.data if self.metallic_roughness_texture else None,
        }  # noqa E501

    @data.setter
    def data(self, data):
        self.base_color_factor = data.get("base_color_factor")
        self.base_color_texture = Texture.from_data(data.get("base_color_texture")) if data.get("base_color_texture") else None  # noqa E501
        self.metallic_factor = data.get("metallic_factor")
        self.roughness_factor = data.get("roughness_factor")
        self.metallic_roughness_texture = Texture.from_data(data.get("metallic_roughness_texture")) if data.get("metallic_roughness_texture") else None  # noqa E501


class Texture(Data):
    def __init__(
        self,
        source=None,
        name=None,
        offset=None,
        rotation=None,
        scale=None,
        repeat=None,
    ):  # noqa E501
        self.source = source
        self.name = name
        self.offset = offset or [0.0, 0.0]
        self.rotation = rotation or 0.0
        self.repeat = repeat or [0, 0]
        self.scale = scale or [1.0, 1.0]

    @property
    def data(self):
        return {
            "source": self.source,
            "name": self.name,
            "offset": self.offset,
            "rotation": self.rotation,
            "repeat": self.repeat,
            "scale": self.scale,
        }

    @data.setter
    def data(self, data):
        if data:
            self.source = data.get("source")
            self.name = data.get("name")
            self.offset = data.get("offset")
            self.rotation = data.get("rotation")
            self.scale = data.get("scale")
            self.repeat = data.get("repeat")


class NormalTexture(Texture):
    def __init__(self, source=None, name=None, scale=None):
        super(NormalTexture, self).__init__(source, name)
        self.scale = scale

    @property
    def data(self):
        data = super(NormalTexture, self).data
        data.update({"scale": self.scale})
        return data

    @data.setter
    def data(self, data):
        if data:
            self.source = data.get("source")
            self.name = data.get("name")
            self.scale = data.get("scale")


class OcclusionTexture(Texture):
    def __init__(self, source=None, name=None, strength=None):
        super(OcclusionTexture, self).__init__(source, name)
        self.strength = strength

    @property
    def data(self):
        data = super(OcclusionTexture, self).data
        data.update({"strength": self.strength})
        return data

    @data.setter
    def data(self, data):
        if data:
            self.source = data.get("source")
            self.name = data.get("name")
            self.strength = data.get("strength")


if __name__ == "__main__":

    import os
    from compas.datastructures import Mesh
    from compas_xr.datastructures import Scene
    from compas_xr import DATA

    gltf_filepath = os.path.join(DATA, "mesh_with_material.gltf")
    glb_filepath = os.path.join(DATA, "mesh_with_material.glb")
    usd_filepath = os.path.join(DATA, "mesh_with_material.usda")

    color = (1.0, 0.4, 0)
    material = Material()
    material.name = "Plaster"
    material.pbr_metallic_roughness = PBRMetallicRoughness()
    material.pbr_metallic_roughness.base_color_factor = list(color) + [1.0]
    material.pbr_metallic_roughness.metallic_factor = 0.0
    material.pbr_metallic_roughness.roughness_factor = 0.5

    scene = Scene()
    world = scene.add_layer("world")
    mkey = scene.add_material(material)
    cmesh = Mesh.from_polyhedron(8)
    scene.add_layer("element", parent=world, element=cmesh, material=mkey)

    scene.to_gltf(gltf_filepath, embed_data=False)
    scene.to_gltf(glb_filepath, embed_data=True)
    scene.to_usd(usd_filepath)

    scene.from_gltf(gltf_filepath)