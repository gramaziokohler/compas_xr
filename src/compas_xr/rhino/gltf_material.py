# https://github.com/Stykka/glTF-Bin/blob/1c707c69118f487fae4f2f593282da6de34659bc/glTF-BinExporter/RhinoMaterialGltfConverter.cs

import compas


from compas.files.gltf.data_classes import TextureData
from compas.files.gltf.data_classes import TextureInfoData
from compas.files.gltf.data_classes import PBRMetallicRoughnessData
from compas.files.gltf.data_classes import MaterialData
from compas.files.gltf.data_classes import NormalTextureInfoData
from compas.files.gltf.data_classes import OcclusionTextureInfoData
from compas.files.gltf.extensions import KHR_materials_transmission
from compas.files.gltf.extensions import KHR_materials_clearcoat

from compas_xr.datastructures.material import Texture

if compas.IPY:
    import System
    from System.Drawing import Bitmap
    from Rhino.DocObjects import TextureType
    from Rhino.Render import RenderMaterial
    import Rhino


"""
from enum import Enum
class AlphaMode(Enum):
    BLEND = 'BLEND'
    MASK = 'MASK'
    OPAQUE = 'OPAQUE'
"""


class AlphaMode(object):
    BLEND = 'BLEND'
    MASK = 'MASK'
    OPAQUE = 'OPAQUE'


class MineType(object):
    JPEG = "image/jpeg"
    PNG = "image/png"


# KHR_materials_transmission
PreProcessGamma = True


# TODO: adding extensions GLTF


def AddMaterial(rhinoMaterial):

    import time

    t0 = time.time()

    material = MaterialData()
    material.name = rhinoMaterial.Name or "Default"
    material.pbr_metallic_roughness = PBRMetallicRoughnessData()

    if not rhinoMaterial.IsPhysicallyBased:
        rhinoMaterial.ToPhysicallyBased()

    pbr = rhinoMaterial.PhysicallyBased

    print("1", time.time() - t0)
    t0 = time.time()

    # Textures
    metallicTexture = pbr.GetTexture(TextureType.PBR_Metallic)
    roughnessTexture = pbr.GetTexture(TextureType.PBR_Roughness)
    normalTexture = pbr.GetTexture(TextureType.Bump)
    occlusionTexture = pbr.GetTexture(TextureType.PBR_AmbientOcclusion)
    emissiveTexture = pbr.GetTexture(TextureType.PBR_Emission)
    opacityTexture = pbr.GetTexture(TextureType.Opacity)
    clearcoatTexture = pbr.GetTexture(TextureType.PBR_Clearcoat)
    clearcoatRoughessTexture = pbr.GetTexture(TextureType.PBR_ClearcoatRoughness)
    clearcoatNormalTexture = pbr.GetTexture(TextureType.PBR_ClearcoatBump)

    print("2", time.time() - t0)
    t0 = time.time()
    HandleBaseColor(rhinoMaterial, material)
    print("3", time.time() - t0)
    t0 = time.time()

    if metallicTexture and roughnessTexture:
        material.pbr_metallic_roughness.metallic_roughness_texture = AddMetallicRoughnessTexture(rhinoMaterial)  # check
        material.pbr_metallic_roughness.metallic_factor = 1.0
        material.pbr_metallic_roughness.roughness_factor = 1.0
    else:
        material.pbr_metallic_roughness.metallic_factor = float(pbr.Metallic)
        material.pbr_metallic_roughness.roughness_factor = float(pbr.Roughness)

    if normalTexture and normalTexture.Enabled:
        material.normal_texture = AddTextureNormal(normalTexture)

    if occlusionTexture and occlusionTexture.Enabled:
        material.occlusion_texture = AddTextureOcclusion(occlusionTexture.FileReference.FullPath)

    if emissiveTexture and emissiveTexture.Enabled:
        material.emissive_texture = AddTexture(emissiveTexture.FileReference.FullPath)
        emissionMultiplier = 1.0
        param = rhinoMaterial.RenderMaterial.GetParameter("emission-multiplier")
        if param:
            emissionMultiplier = float(param)
        material.emissive_factor = [emissionMultiplier, emissionMultiplier, emissionMultiplier]
    else:
        material.emissive_factor = [rhinoMaterial.PhysicallyBased.Emission.R, rhinoMaterial.PhysicallyBased.Emission.G, rhinoMaterial.PhysicallyBased.Emission.B]

    # Extensions
    material.extensions = {}

    transmission = KHR_materials_transmission()
    if opacityTexture and opacityTexture.Enabled:
        transmission.transmission_texture = CreateOpacityTexture(opacityTexture)
        transmission.transmission_factor = 1.0
    else:
        transmission.transmission_factor = 1.0 - float(pbr.Opacity)
    material.extensions.update({"KHR_materials_transmission": transmission})

    clearcoat = KHR_materials_clearcoat()
    if clearcoatTexture and clearcoatTexture.Enabled:
        clearcoat.clearcoat_texture = AddTexture(clearcoatTexture.FileReference.FullPath)
        clearcoat.clearcoat_factor = 1.0
    else:
        clearcoat.clearcoat_factor = float(pbr.Clearcoat)

    if clearcoatRoughessTexture and clearcoatRoughessTexture.Enabled:
        clearcoat.clearcoat_roughness_texture = AddTexture(clearcoatRoughessTexture.FileReference.FullPath)
        clearcoat.clearcoat_roughness_factor = 1.0
    else:
        clearcoat.clearcoat_roughness_factor = float(pbr.ClearcoatRoughness)

    if clearcoatNormalTexture and clearcoatNormalTexture.Enabled:
        clearcoat.clearcoat_normal_texture = AddTextureNormal(clearcoatNormalTexture)

    material.extensions.update({"KHR_materials_clearcoat": clearcoat})

    return material


def CreateOpacityTexture(texture):
    path = texture.FileReference.FullPath
    print(path)
    bmp = Bitmap(path)
    final = Bitmap(bmp.Width, bmp.Height)

    # Transmission texture is stored in an images R channel
    # https://github.com/KhronosGroup/glTF/blob/master/extensions/2.0/Khronos/KHR_materials_transmission/README.md#properties
    for i in range(bmp.Width):
        for j in range(bmp.Height):
            color = Rhino.Display.Color4f(bmp.GetPixel(i, j))
            value = 1.0 - color.L
            r = int(value * 255.0)
            r = max(min(r, 255), 0)
            final.SetPixel(i, j, System.Drawing.Color.FromArgb(r, 0, 0))

    textureIndex = GetTextureFromBitmap(final)
    textureInfo = TextureInfoData(index=textureIndex, tex_coord=0)
    return textureInfo


def HandleBaseColor(rhinoMaterial, gltfMaterial):

    baseColorDoc = rhinoMaterial.GetTexture(TextureType.PBR_BaseColor)
    alphaTextureDoc = rhinoMaterial.GetTexture(TextureType.PBR_Alpha)

    baseColorTexture = rhinoMaterial.RenderMaterial.GetTextureFromUsage(RenderMaterial.StandardChildSlots.PbrBaseColor)
    alphaTexture = rhinoMaterial.RenderMaterial.GetTextureFromUsage(RenderMaterial.StandardChildSlots.PbrAlpha)

    baseColorLinear = False if not baseColorTexture else IsLinear(baseColorTexture)

    hasBaseColorTexture = False if not baseColorDoc else baseColorDoc.Enabled
    hasAlphaTexture = False if not alphaTextureDoc else alphaTextureDoc.Enabled

    baseColorDiffuseAlphaForTransparency = rhinoMaterial.PhysicallyBased.UseBaseColorTextureAlphaForObjectAlphaTransparencyTexture

    baseColor = rhinoMaterial.PhysicallyBased.BaseColor

    baseColor = Rhino.Display.Color4f.ApplyGamma(baseColor, PreProcessGamma)

    if not hasBaseColorTexture and not hasAlphaTexture:
        gltfMaterial.pbr_metallic_roughness = PBRMetallicRoughnessData()
        gltfMaterial.pbr_metallic_roughness.base_color_factor = [baseColor.R, baseColor.G, baseColor.B, float(rhinoMaterial.PhysicallyBased.Alpha)]

        if rhinoMaterial.PhysicallyBased.Alpha == 1.0:
            gltfMaterial.alpha_mode = AlphaMode.OPAQUE
        else:
            gltfMaterial.alpha_mode = AlphaMode.BLEND
    elif hasBaseColorTexture and not hasAlphaTexture:
        gltfMaterial.pbr_metallic_roughness = PBRMetallicRoughnessData()

        texture = Texture(source=baseColorTexture.Filename,  # .FileReference.FullPath
                          name=baseColorTexture.Name,
                          offset=list(baseColorTexture.GetOffset())[:2],
                          rotation=list(baseColorTexture.GetRotation())[0],
                          scale=None,  # baseColorTexture.GetScale()
                          repeat=list(baseColorTexture.GetRepeat())[:2])
        print(texture.data)

        texture, hasAlpha = CombineBaseColorAndAlphaTexture(baseColorTexture, alphaTexture, baseColorDiffuseAlphaForTransparency,
                                                            baseColor, baseColorLinear, float(rhinoMaterial.PhysicallyBased.Alpha))

        gltfMaterial.pbr_metallic_roughness.base_color_texture = texture

        if hasAlpha:
            gltfMaterial.alpha_mode = AlphaMode.BLEND
        else:
            gltfMaterial.alpha_mode = AlphaMode.OPAQUE


def IsLinear(texture):
    attribs = texture.GetType().GetCustomAttributes(False)
    if attribs and attribs.Length > 0:
        return attribs[0].IsLinear
    else:
        return texture.IsLinear()


def CombineBaseColorAndAlphaTexture(baseColorTexture, alphaTexture, baseColorDiffuseAlphaForTransparency, baseColor, baseColorLinear, alpha):

    hasAlpha = False
    hasBaseColorTexture = baseColorTexture is not None
    hasAlphaTexture = alphaTexture is not None

    # print("==============")
    # for x in dir(baseColorTexture):
    #    print("   ", x)
    # print("==============")

    import clr
    v = clr.StrongBox[System.Int32]()
    v.Value = 0

    baseColorWidth, baseColorHeight, baseColorDepth = v, v, v
    alphaWidth, alphaHeight, alphaDepth = v, v, v

    if hasBaseColorTexture:
        baseColorTexture.PixelSize(baseColorWidth, baseColorHeight, baseColorDepth)

    if hasAlphaTexture:
        alphaTexture.PixelSize(alphaWidth, alphaHeight, alphaDepth)

    width = max(baseColorWidth, alphaWidth)
    height = max(baseColorHeight, alphaHeight)

    if width <= 0:
        width = 1024

    if height <= 0:
        height = 1024

    baseColorEvaluator = None

    print("hasBaseColorTexture", hasBaseColorTexture)
    print("hasAlphaTexture", hasAlphaTexture)

    if (hasBaseColorTexture):
        baseColorEvaluator = baseColorTexture.CreateEvaluator(Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal)

    alphaTextureEvaluator = None

    if hasAlphaTexture:
        alphaTextureEvaluator = alphaTexture.CreateEvaluator(Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal)

    print(width, height)
    bitmap = Bitmap(width, height)

    for i in range(width):
        for j in range(height):
            x = i / float(width - 1)
            y = j / float(height - 1)
            y = 1.0 - y
            uvw = Rhino.Geometry.Point3d(x, y, 0.0)

            baseColorOut = baseColor
            if hasBaseColorTexture:
                baseColorOut = baseColorEvaluator.GetColor(uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero)

                if(baseColorLinear):
                    baseColorOut = Rhino.Display.Color4f.ApplyGamma(baseColorOut, PreProcessGamma)

            if not baseColorDiffuseAlphaForTransparency:
                baseColorOut = Rhino.Display.Color4f(baseColorOut.R, baseColorOut.G, baseColorOut.B, 1.0)

            evaluatedAlpha = float(alpha)

            if(hasAlphaTexture):
                alphaColor = alphaTextureEvaluator.GetColor(uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero)
                evaluatedAlpha = alphaColor.L

            alphaFinal = baseColor.A * evaluatedAlpha

            hasAlpha = hasAlpha or alpha != 1.0

            colorFinal = Rhino.Display.Color4f(baseColorOut.R, baseColorOut.G, baseColorOut.B, alphaFinal)

            bitmap.SetPixel(i, j, colorFinal.AsSystemColor())

    # Testing
    print(System.Environment.GetFolderPath(System.Environment.SpecialFolder.MyDocuments))
    # bitmap.Save(System.IO.Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.MyDocuments), "out.png"))

    return GetTextureInfoFromBitmap(bitmap), hasAlpha


def AddTextureToBuffers(texturePath):
    image = GetImageFromFile(texturePath) # noqa F821
    imageIdx = dummy.Images.AddAndReturnIndex(image) # noqa F821
    texture = TextureData(source=imageIdx, sampler=0)
    return dummy.Textures.AddAndReturnIndex(texture) # noqa F821


def AddTexture(texturePath):
    return Texture(source=texturePath)


def AddTextureNormal(normalTexture):  # def private glTFLoader.Schema.MaterialNormalTextureInfo
    textureIdx = AddNormalTexture(normalTexture)
    constant, a0, a1, a2, a3 = normalTexture.GetAlphaBlendValues()  # check?
    return NormalTextureInfoData(textureIdx, tex_coord=0, scale=float(constant))


def AddNormalTexture(normalTexture):
    bmp = Bitmap(normalTexture.FileReference.FullPath)
    if not Rhino.BitmapExtensions.IsNormalMap(bmp, True):  # check?
        bmp = Rhino.BitmapExtensions.ConvertToNormalMap(bmp, True)  # check?
    return GetTextureFromBitmap(bmp)


def AddTextureOcclusion(texturePath):
    textureIdx = AddTextureToBuffers(texturePath)
    return OcclusionTextureInfoData(textureIdx, tex_coord=0, strength=0.9)


def AddMetallicRoughnessTexture(rhinoMaterial):
    metalTexture = rhinoMaterial.PhysicallyBased.GetTexture(TextureType.PBR_Metallic)
    roughnessTexture = rhinoMaterial.PhysicallyBased.GetTexture(TextureType.PBR_Roughness)

    hasMetalTexture = False if not metalTexture else metalTexture.Enabled
    hasRoughnessTexture = False if not roughnessTexture else roughnessTexture.Enabled

    renderTextureMetal = None
    renderTextureRoughness = None

    mWidth = 0
    mHeight = 0
    rWidth = 0
    rHeight = 0

    # Get the textures
    if hasMetalTexture:
        renderTextureMetal = rhinoMaterial.RenderMaterial.GetTextureFromUsage(Rhino.Render.RenderMaterial.StandardChildSlots.PbrMetallic)
        renderTextureMetal.PixelSize(mWidth, mHeight, _w0)  # noqa F821

    if hasRoughnessTexture:
        renderTextureRoughness = rhinoMaterial.RenderMaterial.GetTextureFromUsage(Rhino.Render.RenderMaterial.StandardChildSlots.PbrRoughness)
        renderTextureRoughness.PixelSize(rWidth, rHeight, _w1)  # noqa F821

    width = max(mWidth, rWidth)
    height = max(mHeight, rHeight)

    print(width, height)

    evalMetal = None
    evalRoughness = None

    # Metal
    if hasMetalTexture:
        evalMetal = renderTextureMetal.CreateEvaluator(Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal)

    # Roughness
    if (hasRoughnessTexture):
        evalRoughness = renderTextureRoughness.CreateEvaluator(Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal)

    # Copy Metal to the blue channel, roughness to the green
    bitmap = Bitmap(width, height, System.Drawing.Imaging.PixelFormat.Format32bppArgb)

    metallic = float(rhinoMaterial.PhysicallyBased.Metallic)
    roughness = float(rhinoMaterial.PhysicallyBased.Roughness)

    for j in range(height - 1):
        for i in range(width - 1):

            x = i / float(width - 1)
            y = j / float(height - 1)

            uvw = Rhino.Geometry.Point3d(x, y, 0.0)

            g = 0
            b = 0
            if (hasMetalTexture):
                metal = evalMetal.GetColor(uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero)
                b = metal.L  # rayscale maps, so we want lumonosity
            else:
                b = metallic

            if (hasRoughnessTexture):
                roughnessColor = evalRoughness.GetColor(uvw, Rhino.Geometry.Vector3d.ZAxis, Rhino.Geometry.Vector3d.Zero)
                g = roughnessColor.L  # grayscale maps, so we want lumonosity
            else:
                g = roughness

            color = Rhino.Display.Color4f(0.0, g, b, 1.0)
            bitmap.SetPixel(i, height - j - 1, color.AsSystemColor())

    return GetTextureInfoFromBitmap(bitmap)


def GetTextureFromBitmap(bitmap):
    image = GetImageFromBitmap(bitmap) # noqa F841
    # imageIdx = dummy.Images.AddAndReturnIndex(image)
    imageIdx = 0
    texture = TextureData(source=imageIdx, sampler=0) # noqa F841
    return 0
    # return dummy.Textures.AddAndReturnIndex(texture)


def GetTextureInfoFromBitmap(bitmap):
    textureIdx = GetTextureFromBitmap(bitmap)
    return TextureInfoData(textureIdx, tex_coord=0)


def GetEncoderInfo(mimeType):
    for encoder in System.Drawing.Imaging.ImageCodecInfo.GetImageEncoders():
        if encoder.MimeType == mimeType:
            return encoder


def GetImageFromBitmap(bitmap, binary=False):  # glTFLoader.Schema.Image
    print(bitmap)
    codec_info = GetEncoderInfo(MineType.JPEG)  # noqa F841
    # myEncoderParameters = new EncoderParameters(1);
    # myEncoderParameter = new EncoderParameter(myEncoder, 75L);
    # myEncoderParameters.Param[0] = myEncoderParameter;

    # path = "test.jpg"
    import random

    i = random.randint(0, 100)

    path = System.IO.Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.MyDocuments), "out%i.jpg" % i)
    bitmap.Save(path)
    # expected Stream, got str
    """
    if (binary):
        return GetImageFromBitmapBinary(bitmap)
    else:
        return GetImageFromBitmapText(bitmap)
    """


"""

def GetImageFromBitmapText(bitmap): # glTFLoader.Schema.Image
    imageBytes = GetImageBytes(bitmap)

    textureBuffer = new glTFLoader.Schema.Buffer();

    textureBuffer.Uri = Constants.TextBufferHeader + Convert.ToBase64String(imageBytes);
    textureBuffer.ByteLength = imageBytes.Length;

    int textureBufferIdx = dummy.Buffers.AddAndReturnIndex(textureBuffer);

    // Create bufferviews
    var textureBufferView = new glTFLoader.Schema.BufferView()
    {
        Buffer = textureBufferIdx,
        ByteOffset = 0,
        ByteLength = textureBuffer.ByteLength,
    };
    int textureBufferViewIdx = dummy.BufferViews.AddAndReturnIndex(textureBufferView);

    return ImageData(mime_type=)

    return new glTFLoader.Schema.Image()
    {
        BufferView = textureBufferViewIdx,
        MimeType = glTFLoader.Schema.Image.MimeTypeEnum.image_png,
    };
}

def GetImageFromBitmapBinary(bitmap) # private glTFLoader.Schema.Image
{
    imageBytes = GetImageBytes(bitmap)
    imageBytesOffset = binaryBuffer.Count
    binaryBuffer.AddRange(imageBytes);

    // Create bufferviews
    var textureBufferView = new glTFLoader.Schema.BufferView()
    {
        Buffer = 0,
        ByteOffset = imageBytesOffset,
        ByteLength = imageBytes.Length,
    };
    int textureBufferViewIdx = dummy.BufferViews.AddAndReturnIndex(textureBufferView);

    return new glTFLoader.Schema.Image()
    {
        BufferView = textureBufferViewIdx,
        MimeType = glTFLoader.Schema.Image.MimeTypeEnum.image_png,
    };
}

private byte[] GetImageBytes(Bitmap bitmap)
{
    using (MemoryStream imageStream = new MemoryStream(4096))
    {
        bitmap.Save(imageStream, System.Drawing.Imaging.ImageFormat.Png);

        //Zero pad so its 4 byte aligned
        long mod = imageStream.Position % 4;
        imageStream.Write(Constants.Paddings[mod], 0, Constants.Paddings[mod].Length);

        return imageStream.ToArray();
    }
}

"""
