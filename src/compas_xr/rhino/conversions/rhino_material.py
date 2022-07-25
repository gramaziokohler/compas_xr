import os
import Rhino
import System.Drawing
import compas

from compas.files.gltf.data_classes import (
    MaterialData,
    PBRMetallicRoughnessData,
    AlphaMode,
    TextureInfoData,
    NormalTextureInfoData,
    OcclusionTextureInfoData,
    ImageData,
    TextureData,
    MineType,
)
from compas.files.gltf.extensions import (
    KHR_materials_clearcoat,
    KHR_materials_transmission,
    KHR_materials_specular,
    KHR_materials_ior,
)


class RgbaChannel:
    Red = 0
    Green = 1
    Blue = 2
    Alpha = 3


def IsLinear(texture):
    attribs = texture.GetType().GetCustomAttributes(
        Rhino.Render.CustomRenderContentAttribute()
    )  # correct?
    if attribs is not None and attribs.Length > 0:
        return attribs[0].IsLinear
    else:
        return texture.IsLinear()


def MineTypeFromFileName(filename):
    ext = os.path.splitext(filename)[1].lower()
    switcher = {
        ".png": (MineType.PNG, System.Drawing.Imaging.ImageFormat.Png),
        ".jpg": (MineType.JPEG, System.Drawing.Imaging.ImageFormat.Jpeg),
        ".jpeg": (MineType.JPEG, System.Drawing.Imaging.ImageFormat.Jpeg),
    }
    return switcher.get(ext)


def GetTextureInfoFromBitmap(gltf_content, bitmap, filename, filepath):  # 3x
    textureIdx = GetTextureFromBitmap(gltf_content, bitmap, filename, filepath)
    return TextureInfoData(index=textureIdx)  # , tex_coord=0)


def AddTexture(gltf_content, texturePath):
    textureIdx = AddTextureToBuffers(gltf_content, texturePath)
    return TextureInfoData(textureIdx)  # , tex_coord=0)


def GetTextureWeight(texture):
    constant, _, _, _, _ = texture.GetAlphaBlendValues()
    return float(constant)


def AddNormalTexture(gltf_content, normalTexture):
    bmp = System.Drawing.Bitmap(normalTexture.FileReference.FullPath)
    filename = os.path.basename(normalTexture.FileReference.FullPath)
    filepath = os.path.dirname(normalTexture.FileReference.FullPath)
    if Rhino.BitmapExtensions.IsNormalMap(bmp, True)[0]:
        bmp, _ = Rhino.BitmapExtensions.ConvertToNormalMap(bmp, True)
    return GetTextureFromBitmap(gltf_content, bmp, filename, filepath)


def AddTextureNormal(gltf_content, normalTexture):
    textureIdx = AddNormalTexture(gltf_content, normalTexture)
    weight = GetTextureWeight(normalTexture)
    return NormalTextureInfoData(textureIdx, scale=weight)  # tex_coord=0,


def AddTextureOcclusion(gltf_content, texture):
    textureIdx = AddTextureToBuffers(gltf_content, texture.FileReference.FullPath)
    return OcclusionTextureInfoData(
        textureIdx, strength=GetTextureWeight(texture)
    )  # tex_coord=0,


def GetTextureFromFile(gltf_content, texturePath, minetype_gltf):
    image_name = os.path.basename(texturePath)
    image_data = ImageData(
        name=image_name,
        mime_type=minetype_gltf,
        uri=texturePath,
    )
    imageIdx = gltf_content.add_image(image_data)
    texture = TextureData(source=imageIdx)
    return gltf_content.add_texture(texture)


def AddTextureToBuffers(gltf_content, texturePath):
    if os.path.splitext(texturePath)[1].lower() == ".tiff":
        # convert to png
        bitmap = System.Drawing.Bitmap(texturePath)
        texturePath = os.path.splitext(texturePath)[0] + ".png"
        bitmap.Save(texturePath, System.Drawing.Imaging.ImageFormat.Png)
    minetype_gltf, _ = MineTypeFromFileName(texturePath)
    return GetTextureFromFile(gltf_content, texturePath, minetype_gltf)


def AddMetallicRoughnessTexture(gltf_content, rhinoMaterial, gltfMaterial):
    metalTexture = rhinoMaterial.PhysicallyBased.GetTexture(
        Rhino.DocObjects.TextureType.PBR_Metallic
    )
    roughnessTexture = rhinoMaterial.PhysicallyBased.GetTexture(
        Rhino.DocObjects.TextureType.PBR_Roughness
    )
    hasMetalTexture = False if metalTexture is None else metalTexture.Enabled
    hasRoughnessTexture = (
        False if roughnessTexture is None else roughnessTexture.Enabled
    )
    mWidth, mHeight, rWidth, rHeight = 0, 0, 0, 0
    filepath = None
    if hasMetalTexture:
        renderTextureMetal = rhinoMaterial.RenderMaterial.GetTextureFromUsage(
            Rhino.Render.RenderMaterial.StandardChildSlots.PbrMetallic
        )
        mWidth, mHeight, _w0 = renderTextureMetal.PixelSize()
        evalMetal = renderTextureMetal.CreateEvaluator(
            Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal
        )
        filepath = os.path.dirname(metalTexture.FileName)
    if hasRoughnessTexture:
        renderTextureRoughness = rhinoMaterial.RenderMaterial.GetTextureFromUsage(
            Rhino.Render.RenderMaterial.StandardChildSlots.PbrRoughness
        )
        rWidth, rHeight, _w1 = renderTextureRoughness.PixelSize()
        evalRoughness = renderTextureRoughness.CreateEvaluator(
            Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal
        )
        filepath = os.path.dirname(roughnessTexture.FileName)
    width = max(mWidth, rWidth)
    height = max(mHeight, rHeight)
    # Copy Metal to the blue channel, roughness to the green
    bitmap = System.Drawing.Bitmap(
        width, height, System.Drawing.Imaging.PixelFormat.Format32bppArgb
    )
    for j in range(height - 1):
        for i in range(width - 1):
            x = float(i) / (width - 1)
            y = float(j) / (height - 1)
            uvw = Rhino.Geometry.Point3d(x, y, 0.0)
            g, b = 1.0, 1.0
            if hasMetalTexture:
                b = evalMetal.GetColor(
                    uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero
                ).L  # grayscale maps, so we want lumonosity
            if hasRoughnessTexture:
                g = evalRoughness.GetColor(
                    uvw, Rhino.Geometry.Vector3d.ZAxis, Rhino.Geometry.Vector3d.Zero
                ).L  # grayscale maps, so we want lumonosity
            color = System.Drawing.Color.FromArgb(255, 0, int(g * 255), int(b * 255))
            bitmap.SetPixel(i, height - j - 1, color)

    return GetTextureInfoFromBitmap(
        gltf_content,
        bitmap,
        "%s_metallic_roughness.png" % gltfMaterial.name,
        filepath,
    )


def GetSingleChannelColor(value, channel):
    i = int(value * 255.0)
    i = max(min(i, 255), 0)
    switcher = {
        RgbaChannel.Alpha: System.Drawing.Color.FromArgb(i, 0, 0, 0),
        RgbaChannel.Red: System.Drawing.Color.FromArgb(0, i, 0, 0),
        RgbaChannel.Green: System.Drawing.Color.FromArgb(0, 0, i, 0),
        RgbaChannel.Blue: System.Drawing.Color.FromArgb(0, 0, 0, i),
    }
    return switcher.get(channel, System.Drawing.Color.FromArgb(i, i, i, i))


def GetTextureFromBitmap(gltf_content, bitmap, filename, filepath):
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
    return GetTextureFromFile(gltf_content, texturePath, minetype_gltf)


def GetSingleChannelTexture(gltf_content, texture, channel, invert):
    filepath = os.path.dirname(texture.FileReference.FullPath)
    bmp = System.Drawing.Bitmap(texture.FileReference.FullPath)
    final = System.Drawing.Bitmap(bmp.Width, bmp.Height)
    for i in range(bmp.Width):
        for j in range(bmp.Height):
            color = bmp.GetPixel(i, j)
            color4f = Rhino.Display.Color4f(color)
            print(color)  # should be 4 f
            print(color4f)  # should be 4 f
            value = float(color4f.L)
            if invert:
                value = 1.0 - value
            colorFinal = GetSingleChannelColor(value, channel)
            final.SetPixel(i, j, colorFinal)

    return GetTextureInfoFromBitmap(gltf_content, final, "final.png", filepath)


def CombineBaseColorAndAlphaTexture(
    gltf_content,
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
        baseColorEvaluator = baseColorTexture.CreateEvaluator(
            Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal
        )
    if hasAlphaTexture:
        alphaWidth, alphaHeight, _ = alphaTexture.PixelSize()
        alphaTextureEvaluator = alphaTexture.CreateEvaluator(
            Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal
        )
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
                baseColorOut = baseColorEvaluator.GetColor(
                    uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero
                )
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
                alphaColor = alphaTextureEvaluator.GetColor(
                    uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero
                )
                evaluatedAlpha = alphaColor.L
            alphaFinal = baseColor.A * evaluatedAlpha
            hasAlpha = hasAlpha or (alpha != 1.0)
            colorFinal = baseColorOut[:3] + [alphaFinal]
            r, g, b, a = [int(c * 255) for c in colorFinal]
            colorFinal = System.Drawing.Color.FromArgb(a, r, g, b)
            bitmap.SetPixel(i, j, colorFinal)
    return GetTextureInfoFromBitmap(gltf_content, bitmap, filename, filepath), hasAlpha


def HandleBaseColor(gltf_content, rhinoMaterial, gltfMaterial):
    baseColorDoc = rhinoMaterial.GetTexture(Rhino.DocObjects.TextureType.PBR_BaseColor)
    alphaTextureDoc = rhinoMaterial.GetTexture(Rhino.DocObjects.TextureType.PBR_Alpha)
    baseColorTexture = rhinoMaterial.RenderMaterial.GetTextureFromUsage(
        Rhino.Render.RenderMaterial.StandardChildSlots.PbrBaseColor
    )
    alphaTexture = rhinoMaterial.RenderMaterial.GetTextureFromUsage(
        Rhino.Render.RenderMaterial.StandardChildSlots.PbrAlpha
    )
    hasBaseColorTexture = False if baseColorDoc is None else baseColorDoc.Enabled
    hasAlphaTexture = False if alphaTextureDoc is None else alphaTextureDoc.Enabled
    baseColorDiffuseAlphaForTransparency = (
        rhinoMaterial.PhysicallyBased.UseBaseColorTextureAlphaForObjectAlphaTransparencyTexture
    )
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
        texture_info, hasAlpha = CombineBaseColorAndAlphaTexture(
            gltf_content,
            baseColorTexture,
            alphaTexture,
            baseColorDiffuseAlphaForTransparency,
            baseColor,
            rhinoMaterial.PhysicallyBased.Alpha,
            filename,
            filepath,
        )
        gltfMaterial.pbr_metallic_roughness.base_color_texture = texture_info
        if hasAlpha:
            gltfMaterial.alpha_mode = AlphaMode.BLEND
        else:
            gltfMaterial.alpha_mode = AlphaMode.OPAQUE


def AddMaterial(gltf_content, material):

    rhinoMaterial = material.SimulatedMaterial(
        Rhino.Render.RenderTexture.TextureGeneration.Allow
    )
    renderMaterial = material

    material = MaterialData()
    material.name = (
        renderMaterial.Name.replace(" ", "_") if renderMaterial.Name else "material"
    )
    material.pbr_metallic_roughness = PBRMetallicRoughnessData()

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
    clearcoatRoughessTexture = pbr.GetTexture(
        Rhino.DocObjects.TextureType.PBR_ClearcoatRoughness
    )
    clearcoatNormalTexture = pbr.GetTexture(
        Rhino.DocObjects.TextureType.PBR_ClearcoatBump
    )
    specularTexture = pbr.GetTexture(Rhino.DocObjects.TextureType.PBR_Specular)

    HandleBaseColor(gltf_content, rhinoMaterial, material)

    hasMetalTexture = False if metallicTexture is None else metallicTexture.Enabled
    hasRoughnessTexture = (
        False if roughnessTexture is None else roughnessTexture.Enabled
    )

    if hasMetalTexture or hasRoughnessTexture:
        material.pbr_metallic_roughness.metallic_roughness_texture = (
            AddMetallicRoughnessTexture(gltf_content, rhinoMaterial, material)
        )

    material.pbr_metallic_roughness.metallic_factor = float(pbr.Metallic)
    material.pbr_metallic_roughness.roughness_factor = float(pbr.Roughness)

    if normalTexture is not None and normalTexture.Enabled:
        material.normal_texture = AddTextureNormal(gltf_content, normalTexture)

    if occlusionTexture is not None and occlusionTexture.Enabled:
        material.occlusion_texture = AddTextureOcclusion(gltf_content, occlusionTexture)

    if emissiveTexture is not None and emissiveTexture.Enabled:
        material.emissive_texture = AddTexture(
            gltf_content, emissiveTexture.FileReference.FullPath
        )
        emissionMultiplier = 1.0
        param = rhinoMaterial.RenderMaterial.GetParameter("emission-multiplier")
        if param is not None:
            emissionMultiplier = float(param)
        material.EmissiveFactor = [
            emissionMultiplier,
            emissionMultiplier,
            emissionMultiplier,
        ]
    else:
        material.EmissiveFactor = [
            float(rhinoMaterial.PhysicallyBased.Emission.R),
            float(rhinoMaterial.PhysicallyBased.Emission.G),
            float(rhinoMaterial.PhysicallyBased.Emission.B),
        ]

    # Extensions

    # Opacity => Transmission https://github.com/KhronosGroup/glTF/blob/master/extensions/2.0/Khronos/KHR_materials_transmission/README.md
    transmission = KHR_materials_transmission()
    if opacityTexture is not None and opacityTexture.Enabled:
        # Transmission texture is stored in an images R channel
        # https://github.com/KhronosGroup/glTF/blob/master/extensions/2.0/Khronos/KHR_materials_transmission/README.md#properties
        transmission.transmission_texture = GetSingleChannelTexture(
            gltf_content, opacityTexture, RgbaChannel.Red, True
        )
        transmission.transmission_factor = GetTextureWeight(opacityTexture)
    else:
        transmission.transmission_factor = 1.0 - float(pbr.Opacity)
    material.add_extension(transmission)

    # Clearcoat => Clearcoat https://github.com/KhronosGroup/glTF/blob/master/extensions/2.0/Khronos/KHR_materials_clearcoat/README.md
    clearcoat = KHR_materials_clearcoat()
    if clearcoatTexture is not None and clearcoatTexture.Enabled:
        clearcoat.clearcoat_texture = AddTexture(
            gltf_content, clearcoatTexture.FileReference.FullPath
        )
        clearcoat.clearcoat_factor = GetTextureWeight(clearcoatTexture)
    else:
        clearcoat.clearcoat_factor = float(pbr.Clearcoat)
    if clearcoatRoughessTexture is not None and clearcoatRoughessTexture.Enabled:
        clearcoat.clearcoat_roughness_texture = AddTexture(
            gltf_content, clearcoatRoughessTexture.FileReference.FullPath
        )
        clearcoat.clearcoat_roughness_factor = GetTextureWeight(
            clearcoatRoughessTexture
        )
    else:
        clearcoat.clearcoat_roughness_factor = float(pbr.ClearcoatRoughness)
    if clearcoatNormalTexture is not None and clearcoatNormalTexture.Enabled:
        clearcoat.clearcoat_normal_texture = AddTextureNormal(
            gltf_content, clearcoatNormalTexture
        )
    material.add_extension(clearcoat)

    # Opacity IOR -> IOR https://github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_materials_ior
    ior = KHR_materials_ior(ior=float(pbr.OpacityIOR))
    material.add_extension(ior)

    # Specular -> Specular https://github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_materials_specular
    specular = KHR_materials_specular()
    if specularTexture is not None and specularTexture.Enabled:
        # Specular is stored in the textures alpha channel
        specular.specular_texture = GetSingleChannelTexture(
            gltf_content, specularTexture, RgbaChannel.Alpha, False
        )
        specular.specular_factor = GetTextureWeight(specularTexture)
    else:
        specular.specular_factor = float(pbr.Specular)
    material.add_extension(specular)

    return gltf_content.add_material(material)
