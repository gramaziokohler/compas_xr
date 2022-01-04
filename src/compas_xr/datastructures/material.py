from compas.data import Data

# https://github.com/KhronosGroup/glTF/blob/master/specification/2.0/schema/material.schema.json


class Material(Data):
    """
    """

    def __init__(self,
                 name=None,
                 extras=None,
                 pbr_metallic_roughness=None,
                 normal_texture=None,
                 occlusion_texture=None,
                 emissive_texture=None,
                 emissive_factor=None,
                 alpha_mode=None,
                 alpha_cutoff=None,
                 double_sided=None):
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
        return {'name': self.name,
                'extras': self.extras,
                'pbr_metallic_roughness': self.pbr_metallic_roughness.data,
                'normal_texture': self.normal_texture,
                'occlusion_texture': self.occlusion_texture,
                'emissive_texture': self.emissive_texture,
                'emissive_factor': self.emissive_factor,
                'alpha_mode': self.alpha_mode,
                'alpha_cutoff': self.alpha_cutoff,
                'double_sided': self.double_sided}

    @classmethod
    def from_data(cls, data):
        return cls(name=data.get('name'),
                   extras=data.get('extras'),
                   pbr_metallic_roughness=PBRMetallicRoughness.from_data(data.get('pbrMetallicRoughness')),
                   normal_texture=NormalTexture.from_data(data.get('normalTexture')),
                   occlusion_texture=OcclusionTexture.from_data(data.get('occlusionTexture')),
                   emissive_texture=Texture.from_data(data.get('emissiveTexture')),
                   emissive_factor=data.get('emissiveFactor'),
                   alpha_mode=data.get('alphaMode'),
                   alpha_cutoff=data.get('alphaCutoff'),
                   double_sided=data.get('doubleSided'))


class PBRMetallicRoughness(Data):
    def __init__(self,
                 base_color_factor=None,
                 base_color_texture=None,
                 metallic_factor=None,
                 roughness_factor=None,
                 metallic_roughness_texture=None):
        self.base_color_factor = base_color_factor
        self.base_color_texture = base_color_texture
        self.metallic_factor = metallic_factor
        self.roughness_factor = roughness_factor
        self.metallic_roughness_texture = metallic_roughness_texture

    @property
    def data(self):
        return {'base_color_factor': self.base_color_factor,
                'base_color_texture': self.base_color_texture,
                'metallic_factor': self.metallic_factor,
                'roughness_factor': self.roughness_factor,
                'metallic_roughness_texture': self.metallic_roughness_texture}

    @classmethod
    def from_data(cls, data):
        return cls(base_color_factor=data.get('base_color_factor'),
                   base_color_texture=Texture.from_data(data.get('base_color_texture')),
                   metallic_factor=data.get('metallic_factor'),
                   roughness_factor=data.get('roughness_factor'),
                   metallic_roughness_texture=Texture.from_data(data.get('metallic_roughness_texture')))


class Texture(Data):
    def __init__(self, source=None, name=None, offset=None, rotation=None, scale=None, repeat=None):
        self.source = source
        self.name = name
        self.offset = offset or [0.0, 0.0]
        self.rotation = rotation or 0.
        self.repeat = repeat or [0, 0]
        self.scale = scale or [1., 1.]

    @property
    def data(self):
        return {'source': self.source,
                'name': self.name,
                'offset': self.offset,
                'rotation': self.rotation,
                'repeat': self.repeat,
                'scale': self.scale,
                }

    @classmethod
    def from_data(cls, data):
        return cls(source=data.get('source'),
                   name=data.get('name'),
                   offset=data.get('offset'),
                   rotation=data.get('rotation'),
                   scale=data.get('scale'),
                   repeat=data.get('repeat')
                   )


class NormalTexture(Texture):
    def __init__(self, source=None, name=None, scale=None):
        super(NormalTexture, self).__init__(source, name)
        self.scale = scale

    @property
    def data(self):
        data = super(NormalTexture, self).data
        data.update({'scale': self.scale})
        return data

    @classmethod
    def from_data(cls, data):
        return cls(source=data.get('source'),
                   name=data.get('name'),
                   scale=data.get('scale'))


class OcclusionTexture(Texture):
    def __init__(self, source=None, name=None, strength=None):
        super(OcclusionTexture, self).__init__(source, name)
        self.strength = strength

    @property
    def data(self):
        data = super(OcclusionTexture, self).data
        data.update({'strength': self.strength})
        return data

    @classmethod
    def from_data(cls, data):
        return cls(source=data.get('source'),
                   name=data.get('name'),
                   strength=data.get('strength'))


if __name__ == "__main__":

    import os
    from compas.datastructures import Mesh
    from compas_xr.datastructures import Scene
    from compas_xr import DATA

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
