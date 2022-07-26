from compas.data import Data


class AlphaMode(object):
    """The alpha rendering mode of the material.

    The material's alpha rendering mode enumeration specifying the interpretation of the alpha value of the base color.

    Attributes
    ----------
    OPAQUE : str
        The alpha value is ignored, and the rendered output is fully opaque.
    MASK : str
        The rendered output is either fully opaque or fully transparent depending on the alpha value and the specified `alphaCutoff` value; the exact appearance of the edges
        **MAY** be subject to implementation-specific techniques such as \"`Alpha-to-Coverage`\".
    BLEND : str
        The alpha value is used to composite the source and destination areas. The rendered output is combined with the background using the normal painting operation (i.e. the
        Porter and Duff over operator).
    """

    OPAQUE = "OPAQUE"
    MASK = "MASK"
    BLEND = "BLEND"


class Material(Data):
    """Class for managing a Material.

    The class follows the schema for GLTF materials, as defined in
    https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/schema/material.schema.json


    Attributes
    ----------
    name : str
        The name of the material
    pbr_metallic_roughness : :class:`compas_xr.datastructures.PBRMetallicRoughness`
        A set of parameter values that are used to define the metallic-roughness material model from PBR methodology.
    normal_texture : :class:`compas_xr.datastructures.NormalTexture`
        The normal texture.
    occlusion_texture : :class:`compas_xr.datastructures.OcclusionTexture`
        The occlusion texture.
    emissive_texture : :class:`compas_xr.datastructures.EmissiveTexture`
        The emissive texture.
    emissive_factor : list of 3 float
        The factors for the emissive color of the material.
    alpha_mode : :class:`compas_xr.datastructures.AlphaMode`
        The alpha rendering mode of the material.
    alpha_cutoff : float
        The alpha cutoff value of the material.
    double_sided : bool
        Specifies whether the material is double sided.


    Examples
    --------
    >>> material = Material(name="material")
    >>> material.pbr_metallic_roughness = PBRMetallicRoughness()
    >>> material.pbr_metallic_roughness.base_color_factor = [0.9, 0.4, 0.2, 1.0]
    >>> material.pbr_metallic_roughness.metallic_factor = 0.0
    >>> material.pbr_metallic_roughness.roughness_factor = 0.5
    """

    def __init__(
        self,
        name=None,
        pbr_metallic_roughness=None,
        pbr_specular_glossiness=None,
        normal_texture=None,
        occlusion_texture=None,
        emissive_texture=None,
        emissive_factor=None,
        alpha_mode=None,
        alpha_cutoff=None,
        double_sided=True,
    ):
        self.name = name
        self.pbr_metallic_roughness = pbr_metallic_roughness
        self.pbr_specular_glossiness = pbr_specular_glossiness
        self.normal_texture = normal_texture
        self.occlusion_texture = occlusion_texture
        self.emissive_texture = emissive_texture
        self.emissive_factor = emissive_factor if emissive_factor else [0.0, 0.0, 0.0]
        self.alpha_mode = alpha_mode if alpha_mode is not None else AlphaMode.OPAQUE
        # self.alpha_cutoff = alpha_cutoff if alpha_cutoff is not None else 0.5
        self.alpha_cutoff = alpha_cutoff
        self.double_sided = double_sided if double_sided is not None else True

    @property
    def data(self):
        return {
            "name": self.name,
            "pbr_metallic_roughness": self.pbr_metallic_roughness.data if self.pbr_metallic_roughness else None,  # noqa E501
            "pbr_specular_glossiness": self.pbr_specular_glossiness.data if self.pbr_specular_glossiness else None,  # noqa E501
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
        self.pbr_metallic_roughness = PBRMetallicRoughness.from_data(data.get("pbr_metallic_roughness")) if data.get("pbr_metallic_roughness") else None  # noqa E501
        self.pbr_specular_glossiness = PBRSpecularGlossiness.from_data(data.get("pbr_specular_glossiness")) if data.get("pbr_specular_glossiness") else None  # noqa E501
        self.normal_texture = NormalTexture.from_data(data.get("normal_texture")) if data.get("normal_texture") else None  # noqa E501
        self.occlusion_texture = OcclusionTexture.from_data(data.get("occlusion_texture")) if data.get("occlusion_texture") else None  # noqa E501
        self.emissive_texture = Texture.from_data(data.get("emissive_texture")) if data.get("emissive_texture") else None  # noqa E501 TODO: or TextureInfo?
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
        self.base_color_factor = base_color_factor  # [1.0, 1.0, 1.0, 1.0]
        self.base_color_texture = base_color_texture
        self.metallic_factor = metallic_factor  # 1.0
        self.roughness_factor = roughness_factor  # 1.0
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

        print("base_color_texture", data.get("base_color_texture"))

        self.base_color_texture = TextureInfo.from_data(data.get("base_color_texture")) if data.get("base_color_texture") else None  # noqa E501
        self.metallic_factor = data.get("metallic_factor")
        self.roughness_factor = data.get("roughness_factor")
        self.metallic_roughness_texture = TextureInfo.from_data(data.get("metallic_roughness_texture")) if data.get("metallic_roughness_texture") else None  # noqa E501


class PBRSpecularGlossiness(Data):
    """Class that defines the specular-glossiness material model from Physically-Based Rendering (PBR) methodology.

    https://kcoley.github.io/glTF/extensions/2.0/Khronos/KHR_materials_pbrSpecularGlossiness/schema/glTF.KHR_materials_pbrSpecularGlossiness.schema.json
    """

    def __init__(
        self,
        diffuse_factor=None,
        diffuse_texture=None,
        specular_factor=None,
        glossiness_factor=None,
        specular_glossiness_texture=None,
    ):
        super(PBRSpecularGlossiness, self).__init__()
        self.diffuse_factor = diffuse_factor  # [1.0, 1.0, 1.0, 1.0]
        self.diffuse_texture = diffuse_texture
        self.specular_factor = specular_factor  # [1.0, 1.0, 1.0]
        self.glossiness_factor = glossiness_factor  # 1.0
        self.specular_glossiness_texture = specular_glossiness_texture

    @property
    def data(self):
        return {
            "diffuse_factor": self.diffuse_factor,
            "diffuse_texture": self.diffuse_texture.data if self.diffuse_texture else None,  # noqa E501
            "specular_factor": self.specular_factor,
            "glossiness_factor": self.glossiness_factor,
            "specular_glossiness_texture": self.specular_glossiness_texture.data if self.specular_glossiness_texture else None,
        }  # noqa E501

    @data.setter
    def data(self, data):
        self.diffuse_factor = data.get("diffuse_factor")
        self.diffuse_texture = TextureInfo.from_data(data.get("diffuse_texture")) if data.get("diffuse_texture") else None  # noqa E501
        self.specular_factor = data.get("specular_factor")
        self.glossiness_factor = data.get("glossiness_factor")
        self.specular_glossiness_texture = TextureInfo.from_data(data.get("specular_glossiness_texture")) if data.get("specular_glossiness_texture") else None  # noqa E501


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


class TextureInfo(Data):
    def __init__(self, index=None, tex_coord=None, texture_transform=None):
        super(TextureInfo, self).__init__()
        self.index = index
        self.tex_coord = tex_coord
        self.texture_transform = texture_transform

    @property
    def data(self):
        data = {}
        if self.index is not None:
            data.update({"index": self.index})
        if self.tex_coord is not None:
            data.update({"tex_coord": self.tex_coord})
        if self.texture_transform is not None:
            data.update({"texture_transform": self.texture_transform.data})
        return data

    @data.setter
    def data(self, data):
        if data:
            self.index = data.get("index")
            self.tex_coord = data.get("texCoord")
            self.texture_transform = TextureTransform.from_data(data.get("texture_transform")) if data.get("texture_transform") else None


class NormalTexture(Texture):
    """The tangent space normal texture.

    The texture encodes RGB components with linear transfer function. Each texel represents the XYZ components of a normal vector in tangent space. The normal vectors use the
    convention +X is right and +Y is up. +Z points toward the viewer. If a fourth component (A) is present, it **MUST** be ignored. When undefined, the material does not have a
    tangent space normal texture.
    """

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
    """The occlusion texture.

    The occlusion values are linearly sampled from the R channel. Higher values indicate areas that receive full indirect lighting and lower values indicate no indirect lighting.
    If other channels are present (GBA), they **MUST** be ignored for occlusion calculations. When undefined, the material does not have an occlusion texture.

    https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/schema/material.occlusionTextureInfo.schema.json
    """

    def __init__(self, source=None, name=None, strength=None):
        super(OcclusionTexture, self).__init__(source, name)
        self.strength = strength  # 1.0

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


class TextureTransform(Data):
    """Class that enables shifting and scaling UV coordinates on a per-texture basis.

    https://github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_texture_transform
    """

    def __init__(
        self,
        offset=None,
        rotation=None,
        scale=None,
        tex_coord=None,
    ):
        super(TextureTransform, self).__init__()
        self.offset = offset  # or [0.0, 0.0]
        self.rotation = rotation  # or 0.
        self.scale = scale  # or [1., 1.]
        self.tex_coord = tex_coord

    @property
    def data(self):
        data = {}
        if self.offset is not None:
            data.update({"offset": self.offset})
        if self.rotation is not None:
            data.update({"rotation": self.rotation})
        if self.scale is not None:
            data.update({"scale": self.scale})
        if self.tex_coord is not None:
            data.update({"tex_coord": self.tex_coord})
        return data

    @data.setter
    def data(self, data):
        if data:
            self.offset = data.get("offset")
            self.rotation = data.get("rotation")
            self.scale = data.get("scale")
            self.tex_coord = data.get("texCoord")


class MineType(object):
    JPEG = "image/jpeg"
    PNG = "image/png"


class Image(Data):
    def __init__(
        self,
        uri=None,
        mime_type=None,
        name=None,
    ):
        super(Image, self).__init__()
        self.uri = uri
        self.mime_type = mime_type
        self.name = name

    @property
    def data(self):
        data = {}
        if self.name is not None:
            data.update({"name": self.name})
        if self.mime_type is not None:
            data.update({"mimeType": self.mime_type})
        if self.uri is not None:
            data.update({"uri": self.uri})
        return data

    @data.setter
    def data(self, data):
        if data:
            self.uri = data.get("uri")
            self.mime_type = data.get("mimeType")
            self.name = data.get("name")


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
