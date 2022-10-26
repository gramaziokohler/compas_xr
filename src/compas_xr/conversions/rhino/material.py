import os
import compas

if compas.IPY:
    import Rhino
    import System
    import scriptcontext

import compas

from compas.utilities import color_to_rgb
from compas.utilities import rgb_to_hex

from compas_xr.conversions import BaseMaterial

from compas_xr.datastructures.material import AlphaMode
from compas_xr.datastructures.material import TextureInfo
from compas_xr.datastructures.material import MineType, Image, Texture, NormalTextureInfo, Ior, Transmission, Clearcoat, Specular


def MineTypeFromFileName(filename):
    ext = os.path.splitext(filename)[1].lower()
    switcher = {
        ".png": (MineType.PNG, System.Drawing.Imaging.ImageFormat.Png),
        ".jpg": (MineType.JPEG, System.Drawing.Imaging.ImageFormat.Jpeg),
        ".jpeg": (MineType.JPEG, System.Drawing.Imaging.ImageFormat.Jpeg),
    }
    return switcher.get(ext)


class RGBAChannel:
    Red = 0
    Green = 1
    Blue = 2
    Alpha = 3


class RhinoMaterial(BaseMaterial):
    """RhinoMaterial"""

    @classmethod
    def from_material(cls, material):
        """Construct a material.

        Parameters
        ----------
        material : :class:`compas_xr.datastructures.Material`
        """
        raise NotImplementedError

    def to_compas(self):
        """Convert to a COMPAS object.

        Returns
        -------
        :class:`compas_xr.datastructures.Material`
            A COMPAS material.
        """

        from compas_xr.datastructures import Material
        from compas_xr.datastructures import PBRMetallicRoughness

        if not self.material:
            return None

        rhinoMaterial = self.material.SimulatedMaterial(Rhino.Render.RenderTexture.TextureGeneration.Allow)
        renderMaterial = self.material

        material = Material()
        material.name = renderMaterial.Name.replace(" ", "_") if renderMaterial.Name else "material"
        material.pbr_metallic_roughness = PBRMetallicRoughness()

        if not rhinoMaterial.IsPhysicallyBased:
            rhinoMaterial.ToPhysicallyBased()

        pbr = rhinoMaterial.PhysicallyBased
        metallicTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_Metallic)
        roughnessTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_Roughness)
        normalTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.Bump)
        occlusionTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_AmbientOcclusion)
        emissiveTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_Emission)
        opacityTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.Opacity)
        clearcoatTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_Clearcoat)
        clearcoatRoughessTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_ClearcoatRoughness)
        clearcoatNormalTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_ClearcoatBump)
        specularTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_Specular)

        self.HandleBaseColor(rhinoMaterial, material)

        hasMetalTexture = False if metallicTexture is None else metallicTexture.Enabled
        hasRoughnessTexture = False if roughnessTexture is None else roughnessTexture.Enabled

        if hasMetalTexture or hasRoughnessTexture:
            material.pbr_metallic_roughness.metallic_roughness_texture = self.AddMetallicRoughnessTexture(rhinoMaterial, material)

        material.pbr_metallic_roughness.metallic_factor = float(pbr.Metallic)
        material.pbr_metallic_roughness.roughness_factor = float(pbr.Roughness)

        if normalTexture is not None and normalTexture.Enabled:
            material.normal_texture = self.AddTextureNormal(normalTexture)

        if occlusionTexture is not None and occlusionTexture.Enabled:
            material.occlusion_texture = self.AddTextureOcclusion(occlusionTexture)

        if emissiveTexture is not None and emissiveTexture.Enabled:
            material.emissive_texture = self.AddTexture(emissiveTexture.FileReference.FullPath)
            emissionMultiplier = 1.0
            param = rhinoMaterial.RenderMaterial.GetParameter("emission-multiplier")
            if param is not None:
                emissionMultiplier = float(param)
            material.emissive_factor = [
                emissionMultiplier,
                emissionMultiplier,
                emissionMultiplier,
            ]
        else:
            material.emissive_factor = [
                float(rhinoMaterial.PhysicallyBased.Emission.R),
                float(rhinoMaterial.PhysicallyBased.Emission.G),
                float(rhinoMaterial.PhysicallyBased.Emission.B),
            ]

        material.transmission = Transmission()
        if opacityTexture is not None and opacityTexture.Enabled:
            # Transmission texture is stored in an images R channel
            material.transmission.transmission_texture = self.GetSingleChannelTexture(opacityTexture, RGBAChannel.Red, True)
            material.transmission.transmission_factor = self.GetTextureWeight(opacityTexture)
        else:
            material.transmission.transmission_factor = 1.0 - float(pbr.Opacity)

        material.clearcoat = Clearcoat()
        if clearcoatTexture is not None and clearcoatTexture.Enabled:
            material.clearcoat.clearcoat_texture = self.AddTexture(clearcoatTexture.FileReference.FullPath)
            material.clearcoat.clearcoat_factor = self.GetTextureWeight(clearcoatTexture)
        else:
            material.clearcoat.clearcoat_factor = float(pbr.Clearcoat)
        if clearcoatRoughessTexture is not None and clearcoatRoughessTexture.Enabled:
            material.clearcoat.clearcoat_roughness_texture = self.AddTexture(clearcoatRoughessTexture.FileReference.FullPath)
            material.clearcoat.clearcoat_roughness_factor = self.GetTextureWeight(clearcoatRoughessTexture)
        else:
            material.clearcoat.clearcoat_roughness_factor = float(pbr.ClearcoatRoughness)
        if clearcoatNormalTexture is not None and clearcoatNormalTexture.Enabled:
            material.clearcoat.clearcoat_normal_texture = self.AddTextureNormal(clearcoatNormalTexture)

        material.ior = Ior(ior=float(pbr.OpacityIOR))

        material.specular = Specular()
        if specularTexture is not None and specularTexture.Enabled:
            # Specular is stored in the textures alpha channel
            material.specular.specular_texture = self.GetSingleChannelTexture(specularTexture, RGBAChannel.Alpha, False)
            material.specular.specular_factor = self.GetTextureWeight(specularTexture)
        else:
            material.specular.specular_factor = float(pbr.Specular)

        return material

    def HandleBaseColor(self, rhinoMaterial, gltfMaterial):
        baseColorDoc = rhinoMaterial.GetTexture(Rhino.DocObjects.TextureType.PBR_BaseColor)
        alphaTextureDoc = rhinoMaterial.GetTexture(Rhino.DocObjects.TextureType.PBR_Alpha)
        baseColorTexture = rhinoMaterial.RenderMaterial.GetTextureFromUsage(Rhino.Render.RenderMaterial.StandardChildSlots.PbrBaseColor)
        alphaTexture = rhinoMaterial.RenderMaterial.GetTextureFromUsage(Rhino.Render.RenderMaterial.StandardChildSlots.PbrAlpha)
        hasBaseColorTexture = False if baseColorDoc is None else baseColorDoc.Enabled
        hasAlphaTexture = False if alphaTextureDoc is None else alphaTextureDoc.Enabled
        baseColorDiffuseAlphaForTransparency = rhinoMaterial.PhysicallyBased.UseBaseColorTextureAlphaForObjectAlphaTransparencyTexture
        baseColor = rhinoMaterial.PhysicallyBased.BaseColor
        if not hasBaseColorTexture and not hasAlphaTexture:
            gltfMaterial.pbr_metallic_roughness.base_color_factor = [
                float(baseColor.R),
                float(baseColor.G),
                float(baseColor.B),
                float(rhinoMaterial.PhysicallyBased.Alpha),
            ]
            if rhinoMaterial.PhysicallyBased.Alpha == 1.0:
                gltfMaterial.alpha_mode = AlphaMode.OPAQUE
            else:
                gltfMaterial.alpha_mode = AlphaMode.BLEND
        else:
            if hasBaseColorTexture:
                filename = os.path.basename(baseColorDoc.FileName)
                filepath = os.path.dirname(baseColorDoc.FileName)
            elif hasAlphaTexture:
                filename = os.path.basename(alphaTextureDoc.FileName)
                filepath = os.path.dirname(alphaTextureDoc.FileName)
            else:
                filename = "%s_base_color.png" % gltfMaterial.name
                filepath = None
            texture_info, hasAlpha = self.CombineBaseColorAndAlphaTexture(
                baseColorTexture, alphaTexture, baseColorDiffuseAlphaForTransparency, baseColor, rhinoMaterial.PhysicallyBased.Alpha, filename, filepath
            )
            gltfMaterial.pbr_metallic_roughness.base_color_texture = texture_info
            if hasAlpha:
                gltfMaterial.alpha_mode = AlphaMode.BLEND
            else:
                gltfMaterial.alpha_mode = AlphaMode.OPAQUE

    def CombineBaseColorAndAlphaTexture(
        self,
        baseColorTexture,
        alphaTexture,
        baseColorDiffuseAlphaForTransparency,
        baseColor,
        alpha,
        filename,
        filepath=None,
    ):

        hasAlpha = False
        hasBaseColorTexture = baseColorTexture is not None
        hasAlphaTexture = alphaTexture is not None

        baseColorWidth, baseColorHeight = 0, 0
        alphaWidth, alphaHeight = 0, 0

        if hasBaseColorTexture:
            baseColorWidth, baseColorHeight, _ = baseColorTexture.PixelSize()
            baseColorEvaluator = baseColorTexture.CreateEvaluator(Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal)
        if hasAlphaTexture:
            alphaWidth, alphaHeight, _ = alphaTexture.PixelSize()
            alphaTextureEvaluator = alphaTexture.CreateEvaluator(Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal)
        width = max(baseColorWidth, alphaWidth)
        height = max(baseColorHeight, alphaHeight)

        if width <= 0:
            width = 1024
        if height <= 0:
            height = 1024

        bitmap = System.Drawing.Bitmap(width, height)

        for i in range(width):
            for j in range(height):
                x = float(i) / (width - 1)
                y = float(j) / (height - 1)
                y = 1.0 - y
                uvw = Rhino.Geometry.Point3d(x, y, 0.0)
                baseColorOut = baseColor
                if hasBaseColorTexture:
                    baseColorOut = baseColorEvaluator.GetColor(uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero)
                    baseColorOut = [
                        float(baseColorOut.R),
                        float(baseColorOut.G),
                        float(baseColorOut.B),
                        float(baseColorOut.A),
                    ]
                if not baseColorDiffuseAlphaForTransparency:
                    if type(baseColorOut) == Rhino.Display.Color4f:
                        baseColorOut = [
                            float(baseColorOut.R),
                            float(baseColorOut.G),
                            float(baseColorOut.B),
                            1.0,
                        ]
                    else:
                        baseColorOut[3] = 1.0

                evaluatedAlpha = float(alpha)
                if hasAlphaTexture:
                    alphaColor = alphaTextureEvaluator.GetColor(uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero)
                    evaluatedAlpha = alphaColor.L
                alphaFinal = baseColor.A * evaluatedAlpha
                hasAlpha = hasAlpha or (alpha != 1.0)
                colorFinal = baseColorOut[:3] + [alphaFinal]
                r, g, b, a = [int(c * 255) for c in colorFinal]
                colorFinal = System.Drawing.Color.FromArgb(a, r, g, b)
                bitmap.SetPixel(i, j, colorFinal)
        return self.GetTextureInfoFromBitmap(bitmap, filename, filepath), hasAlpha

    def GetTextureInfoFromBitmap(self, bitmap, filename, filepath):  # 3x
        # textureIdx = self.GetTextureFromBitmap(bitmap, filename, filepath)
        # return TextureInfo(index=textureIdx)  # , tex_coord=0)
        texture = self.GetTextureFromBitmap(bitmap, filename, filepath)
        return TextureInfo(index=texture)  # not index!

    def GetTextureFromBitmap(self, bitmap, filename, filepath):
        if not filepath:
            filepath = os.path.join(compas.APPDATA, "data", "gltfs")

        if os.path.splitext(filename)[1].lower() == ".tiff":
            filename = os.path.splitext(filename)[0] + ".png"

        texturePath = os.path.join(filepath, filename)
        minetype_gltf, minetype_sys = MineTypeFromFileName(texturePath)
        try:
            bitmap.Save(texturePath, minetype_sys)
        except:  # noqa E722
            pass
        return self.GetTextureFromFile(texturePath, minetype_gltf)

    def GetTextureFromFile(self, texturePath, minetype_gltf):
        image_name = os.path.basename(texturePath)
        image_data = Image(
            name=image_name,
            mime_type=minetype_gltf,
            uri=texturePath,
        )
        # imageIdx = self.add_image(image_data)
        # texture = Texture(source=imageIdx)
        texture = Texture(source=image_data)
        # return self.add_texture(texture)
        return texture

    def AddMetallicRoughnessTexture(self, rhinoMaterial, material):
        metalTexture = rhinoMaterial.PhysicallyBased.GetTexture(Rhino.DocObjects.TextureType.PBR_Metallic)
        roughnessTexture = rhinoMaterial.PhysicallyBased.GetTexture(Rhino.DocObjects.TextureType.PBR_Roughness)
        hasMetalTexture = False if metalTexture is None else metalTexture.Enabled
        hasRoughnessTexture = False if roughnessTexture is None else roughnessTexture.Enabled
        mWidth, mHeight, rWidth, rHeight = 0, 0, 0, 0
        filepath = None
        if hasMetalTexture:
            renderTextureMetal = rhinoMaterial.RenderMaterial.GetTextureFromUsage(Rhino.Render.RenderMaterial.StandardChildSlots.PbrMetallic)
            mWidth, mHeight, _w0 = renderTextureMetal.PixelSize()
            evalMetal = renderTextureMetal.CreateEvaluator(Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal)
            filepath = os.path.dirname(metalTexture.FileName)
        if hasRoughnessTexture:
            renderTextureRoughness = rhinoMaterial.RenderMaterial.GetTextureFromUsage(Rhino.Render.RenderMaterial.StandardChildSlots.PbrRoughness)
            rWidth, rHeight, _w1 = renderTextureRoughness.PixelSize()
            evalRoughness = renderTextureRoughness.CreateEvaluator(Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal)
            filepath = os.path.dirname(roughnessTexture.FileName)
        width = max(mWidth, rWidth)
        height = max(mHeight, rHeight)
        # Copy Metal to the blue channel, roughness to the green
        bitmap = System.Drawing.Bitmap(width, height, System.Drawing.Imaging.PixelFormat.Format32bppArgb)
        for j in range(height - 1):
            for i in range(width - 1):
                x = float(i) / (width - 1)
                y = float(j) / (height - 1)
                uvw = Rhino.Geometry.Point3d(x, y, 0.0)
                g, b = 1.0, 1.0
                if hasMetalTexture:
                    b = evalMetal.GetColor(uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero).L  # grayscale maps, so we want lumonosity
                if hasRoughnessTexture:
                    g = evalRoughness.GetColor(uvw, Rhino.Geometry.Vector3d.ZAxis, Rhino.Geometry.Vector3d.Zero).L  # grayscale maps, so we want lumonosity
                color = System.Drawing.Color.FromArgb(255, 0, int(g * 255), int(b * 255))
                bitmap.SetPixel(i, height - j - 1, color)

        return self.GetTextureInfoFromBitmap(bitmap, "%s_metallic_roughness.png" % material.name, filepath)

    def GetTextureWeight(self, texture):
        constant, _, _, _, _ = texture.GetAlphaBlendValues()
        return float(constant)

    def AddNormalTexture(self, normalTexture):
        bmp = System.Drawing.Bitmap(normalTexture.FileReference.FullPath)
        filename = os.path.basename(normalTexture.FileReference.FullPath)
        filepath = os.path.dirname(normalTexture.FileReference.FullPath)
        if Rhino.BitmapExtensions.IsNormalMap(bmp, True)[0]:
            bmp, _ = Rhino.BitmapExtensions.ConvertToNormalMap(bmp, True)
        return self.GetTextureFromBitmap(bmp, filename, filepath)

    def AddTextureNormal(self, normalTexture):
        # textureIdx = self.AddNormalTexture(normalTexture)
        texture = self.AddNormalTexture(normalTexture)
        weight = self.GetTextureWeight(normalTexture)
        # return NormalTextureInfoData(textureIdx, scale=weight)  # tex_coord=0,
        return NormalTextureInfo(index=texture, scale=weight)  # tex_coord=0,

    @classmethod
    def from_object(cls, obj):
        source = obj.Attributes.MaterialSource
        if source == Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject:
            return cls(material=obj.RenderMaterial)
        elif source == Rhino.DocObjects.ObjectMaterialSource.MaterialFromLayer:
            layer_index = obj.Attributes.LayerIndex
            return cls.from_layer(layer_index)
        else:
            return cls()
        # object_color = GetObjectColor(obj)
        # return CreateSolidColorMaterial(object_color, gltf_content)

    @classmethod
    def color_from_object(cls, obj):
        if obj.Attributes.ColorSource == Rhino.DocObjects.ObjectColorSource.ColorFromLayer:
            layerIndex = obj.Attributes.LayerIndex
            color = obj.Document.Layers[layerIndex].Color
        else:
            color = obj.Attributes.ObjectColor
        r, g, b = color_to_rgb((color.R, color.G, color.B), normalize=True)
        a, _, _ = color_to_rgb((color.A, 0, 0), normalize=True)
        return [r, g, b, a]

    @classmethod
    def name_from_color(cls, color):
        r, g, b, a = color
        hex = rgb_to_hex((r, g, b))
        return "color%s%i" % (hex[1:], a * 255)

    @classmethod
    def from_layer(cls, layer_index):
        if layer_index < 0 or layer_index >= scriptcontext.doc.Layers.Count:
            return cls(material=Rhino.DocObjects.Material.DefaultMaterial.RenderMaterial)  # default material
        else:
            return cls(material=scriptcontext.doc.Layers[layer_index].RenderMaterial)
