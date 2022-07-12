import os
import Rhino
import System.Drawing
from compas_rhino import unload_modules


from compas.files.gltf.data_classes import (
    MaterialData,
    PBRMetallicRoughnessData,
    AlphaMode,
    TextureInfoData,
    NormalTextureInfoData,
    OcclusionTextureInfoData,
)
from compas.files.gltf.extensions import (
    KHR_materials_pbrSpecularGlossiness,
    KHR_Texture_Transform,
    KHR_materials_clearcoat,
    KHR_materials_transmission,
    KHR_materials_specular,
)
from compas.files.gltf.data_classes import (
    MaterialData,
    PBRMetallicRoughnessData,
    TextureInfoData,
    ImageData,
    TextureData,
    ImageData,
    MineType,
)
from compas.files.gltf import GLTFContent


class RgbaChannel:
    Red = 0
    Green = 1
    Blue = 2
    Alpha = 3


def IsLinear(texture):
    attribs = texture.GetType().GetCustomAttributes()
    print("attribs", attribs)
    if attribs != None and attribs.Length > 0:
        return attribs[0].IsLinear
    else:
        return texture.IsLinear()


def GetTextureInfoFromBitmap(bitmap):
    textureIdx = GetTextureFromBitmap(bitmap)
    return TextureInfoData(index=textureIdx, tex_coord=0)


def AddTexture(texturePath):
    textureIdx = AddTextureToBuffers(texturePath)
    return TextureInfoData(textureIdx, tex_coord=0)


def GetTextureWeight(texture):
    constant, a0, a1, a2, a3 = texture.GetAlphaBlendValues()
    return float(constant)


def AddNormalTexture(normalTexture):
    bmp = System.Drawing.Bitmap(normalTexture.FileReference.FullPath)
    if not Rhino.BitmapExtensions.IsNormalMap(bmp, True):  # todo check
        bmp, pZ = Rhino.BitmapExtensions.ConvertToNormalMap(bmp, True)
    return GetTextureFromBitmap(bmp)


def AddTextureNormal(normalTexture):
    textureIdx = AddNormalTexture(normalTexture)
    weight = GetTextureWeight(normalTexture)
    return NormalTextureInfoData(textureIdx, tex_coord=0, scale=weight)


def GetImageBytes(bitmap):

    with MemoryStream(4096) as imageStream:
        bitmap.Save(imageStream, System.Drawing.Imaging.ImageFormat.Png)
        # Zero pad so its 4 byte aligned
        mod = imageStream.Position % 4
        imageStream.Write(Constants.Paddings[mod], 0, Constants.Paddings[mod].Length)
        return imageStream.ToArray()


def AddTextureOcclusion(texture):
    textureIdx = AddTextureToBuffers(texture.FileReference.FullPath)
    return OcclusionTextureInfoData(
        textureIdx, tex_coord=0, strength=GetTextureWeight(texture)
    )


def AddTextureToBuffers(gltf_content, texturePath):
    print("texturePath", texturePath)
    # image = GetImageFromFile(texturePath)

    image_name = os.path.basename(texturePath)

    image_data = ImageData(
        name=image_name,
        mime_type="image/jpeg",  # TODO
        uri=texturePath,
    )

    imageIdx = gltf_content.add_image(image_data)
    texture = TextureData(source=imageIdx)  # sampler=0

    return gltf_content.add_texture(texture)


def AddMetallicRoughnessTexture(rhinoMaterial):
    metalTexture = rhinoMaterial.PhysicallyBased.GetTexture(
        Rhino.DocObjects.TextureType.PBR_Metallic
    )
    roughnessTexture = rhinoMaterial.PhysicallyBased.GetTexture(
        Rhino.DocObjects.TextureType.PBR_Roughness
    )

    hasMetalTexture = False if metalTexture == None else metalTexture.Enabled
    hasRoughnessTexture = (
        False if roughnessTexture == None else roughnessTexture.Enabled
    )

    renderTextureMetal = None
    renderTextureRoughness = None

    mWidth = 0
    mHeight = 0
    rWidth = 0
    rHeight = 0

    if hasMetalTexture:
        renderTextureMetal = rhinoMaterial.RenderMaterial.GetTextureFromUsage(
            Rhino.Render.RenderMaterial.StandardChildSlots.PbrMetallic
        )
        mWidth, mHeight, _w0 = renderTextureMetal.PixelSize()

    if hasRoughnessTexture:
        renderTextureRoughness = rhinoMaterial.RenderMaterial.GetTextureFromUsage(
            Rhino.Render.RenderMaterial.StandardChildSlots.PbrRoughness
        )
        rWidth, rHeight, _w1 = renderTextureRoughness.PixelSize()

    width = max(mWidth, rWidth)
    height = max(mHeight, rHeight)

    evalMetal = None
    evalRoughness = None

    if hasMetalTexture:
        evalMetal = renderTextureMetal.CreateEvaluator(
            Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal
        )

    if hasRoughnessTexture:
        evalRoughness = renderTextureRoughness.CreateEvaluator(
            Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal
        )

    # Copy Metal to the blue channel, roughness to the green
    bitmap = System.Drawing.Bitmap(
        width, height, System.Drawing.Imaging.PixelFormat.Format32bppArgb
    )

    for j in range(height - 1):
        for i in range(width - 1):
            x = float(i) / (width - 1)
            y = float(j) / (height - 1)
            uvw = Rhino.Geometry.Point3d(x, y, 0.0)

            g = 1.0
            b = 1.0

            if hasMetalTexture:
                metal = evalMetal.GetColor(
                    uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero
                )
                b = metal.L  # grayscale maps, so we want lumonosity

            if hasRoughnessTexture:
                roughnessColor = evalRoughness.GetColor(
                    uvw, Rhino.Geometry.Vector3d.ZAxis, Rhino.Geometry.Vector3d.Zero
                )
                g = roughnessColor.L  # grayscale maps, so we want lumonosity

            color = System.Drawing.Color.FromArgb(0, int(g * 255), int(b * 255), 255)
            bitmap.SetPixel(i, height - j - 1, color)

    return GetTextureInfoFromBitmap(bitmap)


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


def GetImageFromBitmapBinary(bitmap, gltf_content):

    imageBytes = GetImageBytes(bitmap)
    imageBytesOffset = int(binaryBuffer.Count)
    binaryBuffer.AddRange(imageBytes)

    # Create bufferviews
    textureBufferView = BufferView(
        buffer=0,
        ByteOffset=imageBytesOffset,
        ByteLength=imageBytes.Length,
    )
    textureBufferViewIdx = gltf_content.BufferViews.AddAndReturnIndex(textureBufferView)

    image = ImageData(mime_type=MineType.JPEG)
    # image.buffer_view = textureBufferViewIdx # how to pass this when to_data?

    return image


def GetImageFromBitmap(bitmap, binary=False):
    if binary:
        return GetImageFromBitmapBinary(bitmap)
    else:
        return GetImageFromBitmapText(bitmap)  # ImageData


def GetTextureFromBitmap(bitmap, gltf_content):
    image = GetImageFromBitmap(bitmap)
    imageIdx = gltf_content.add_image(image)
    texture = TextureData(sampler=0, source=imageIdx)
    return gltf_content.add_texture(texture)


def GetSingleChannelTexture(texture, channel, invert):
    print("GetSingleChannelTexture")
    path = texture.FileReference.FullPath
    bmp = System.Drawing.Bitmap(path)
    final = System.Drawing.Bitmap(bmp.Width, bmp.Height)

    for i in range(bmp.Width):
        for j in range(bmp.Height):
            color = bmp.GetPixel(i, j)
            print(color)  # should be 4 f
            value = float(color.L)
            if invert:
                value = 1.0 - value
            colorFinal = GetSingleChannelColor(value, channel)
            final.SetPixel(i, j, colorFinal)
    textureIndex = GetTextureFromBitmap(final)
    return TextureInfoData(textureIndex, tex_coord=0)


def CombineBaseColorAndAlphaTexture(
    baseColorTexture,
    alphaTexture,
    baseColorDiffuseAlphaForTransparency,
    baseColor,
    baseColorLinear,
    alpha,
):

    hasAlpha = False
    hasBaseColorTexture = baseColorTexture is not None
    hasAlphaTexture = alphaTexture is not None

    baseColorWidth, baseColorHeight, baseColorDepth = 0, 0, 0
    alphaWidth, alphaHeight, alphaDepth = 0, 0, 0

    if hasBaseColorTexture:
        # baseColorTexture.PixelSize(out baseColorWidth, out baseColorHeight, out baseColorDepth);
        baseColorWidth, baseColorHeight, baseColorDepth = baseColorTexture.PixelSize()

    if hasAlphaTexture:
        alphaWidth, alphaHeight, alphaDepth = alphaTexture.PixelSize()

    width = max(baseColorWidth, alphaWidth)
    height = max(baseColorHeight, alphaHeight)

    if width <= 0:
        width = 1024
    if height <= 0:
        height = 1024

    baseColorEvaluator = None
    if hasBaseColorTexture:
        baseColorEvaluator = baseColorTexture.CreateEvaluator(
            Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal
        )

    alphaTextureEvaluator = None
    if hasAlphaTexture:
        alphaTextureEvaluator = alphaTexture.CreateEvaluator(
            Rhino.Render.RenderTexture.TextureEvaluatorFlags.Normal
        )

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
                if baseColorLinear:
                    # baseColorOut = Color4f.ApplyGamma(baseColorOut, workflow.PreProcessGamma)
                    raise NotImplementedError

            if not baseColorDiffuseAlphaForTransparency:
                baseColorOut = [baseColorOut.R, baseColorOut.G, baseColorOut.B, 1.0]

            evaluatedAlpha = float(alpha)

            if hasAlphaTexture:
                alphaColor = alphaTextureEvaluator.GetColor(
                    uvw, Rhino.Geometry.Vector3d.Zero, Rhino.Geometry.Vector3d.Zero
                )
                evaluatedAlpha = alphaColor.L

            alphaFinal = baseColor.A * evaluatedAlpha

            hasAlpha = hasAlpha or alpha is not 1.0

            colorFinal = [baseColorOut.R, baseColorOut.G, baseColorOut.B, alphaFinal]
            # does that work?
            bitmap.SetPixel(i, j, colorFinal.AsSystemColor())

    # Testing
    # bitmap.Save(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "out.png"));

    return GetTextureInfoFromBitmap(bitmap), hasAlpha


def HandleBaseColor(rhinoMaterial, gltfMaterial, workflow):
    baseColorDoc = rhinoMaterial.GetTexture(Rhino.DocObjects.TextureType.PBR_BaseColor)
    alphaTextureDoc = rhinoMaterial.GetTexture(Rhino.DocObjects.TextureType.PBR_Alpha)

    baseColorTexture = rhinoMaterial.RenderMaterial.GetTextureFromUsage(
        Rhino.Render.RenderMaterial.StandardChildSlots.PbrBaseColor
    )
    alphaTexture = rhinoMaterial.RenderMaterial.GetTextureFromUsage(
        Rhino.Render.RenderMaterial.StandardChildSlots.PbrAlpha
    )

    baseColorLinear = False if baseColorTexture == None else IsLinear(baseColorTexture)

    hasBaseColorTexture = False if baseColorDoc == None else baseColorDoc.Enabled
    hasAlphaTexture = False if alphaTextureDoc == None else alphaTextureDoc.Enabled

    baseColorDiffuseAlphaForTransparency = (
        rhinoMaterial.PhysicallyBased.UseBaseColorTextureAlphaForObjectAlphaTransparencyTexture
    )

    baseColor = rhinoMaterial.PhysicallyBased.BaseColor

    if workflow.PreProcessColors:
        # baseColor = Color4f.ApplyGamma(baseColor, workflow.PreProcessGamma)
        raise NotImplementedError

    if not hasBaseColorTexture and not hasAlphaTexture:
        gltfMaterial.PbrMetallicRoughness.BaseColorFactor = [
            baseColor.R,
            baseColor.G,
            baseColor.B,
            float(rhinoMaterial.PhysicallyBased.Alpha),
        ]

        if rhinoMaterial.PhysicallyBased.Alpha == 1.0:
            gltfMaterial.alpha_mode = AlphaMode.OPAQUE
        else:
            gltfMaterial.alpha_mode = AlphaMode.BLEND

    else:
        texture_info, hasAlpha = CombineBaseColorAndAlphaTexture(
            baseColorTexture,
            alphaTexture,
            baseColorDiffuseAlphaForTransparency,
            baseColor,
            baseColorLinear,
            rhinoMaterial.PhysicallyBased.Alpha,
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
    material.name = renderMaterial.Name
    material.pbr_metallic_roughness = PBRMetallicRoughnessData()

    if not rhinoMaterial.IsPhysicallyBased:
        rhinoMaterial.ToPhysicallyBased()

    pbr = rhinoMaterial.PhysicallyBased

    # Textures
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

    HandleBaseColor(rhinoMaterial, material)

    hasMetalTexture = False if metallicTexture == None else metallicTexture.Enabled
    hasRoughnessTexture = (
        False if roughnessTexture == None else roughnessTexture.Enabled
    )

    if hasMetalTexture or hasRoughnessTexture:
        material.pbr_metallic_roughness.metallic_roughness_texture = (
            AddMetallicRoughnessTexture(rhinoMaterial)
        )
        metallic = (
            float(pbr.Metallic)
            if metallicTexture == None
            else GetTextureWeight(metallicTexture)
        )
        roughness = (
            float(pbr.Roughness)
            if roughnessTexture == None
            else GetTextureWeight(roughnessTexture)
        )
        material.pbr_metallic_roughness.metallic_factor = metallic
        material.pbr_metallic_roughness.roughness_factor = roughness

    else:
        material.pbr_metallic_roughness.metallic_factor = float(pbr.Metallic)
        material.pbr_metallic_roughness.roughness_factor = float(pbr.Roughness)

    if normalTexture is not None and normalTexture.Enabled:
        material.normal_texture = AddTextureNormal(normalTexture)

    if occlusionTexture is not None and occlusionTexture.Enabled:
        material.occlusion_texture = AddTextureOcclusion(occlusionTexture)

    if emissiveTexture is not None and emissiveTexture.Enabled:
        material.emissive_texture = AddTexture(emissiveTexture.FileReference.FullPath)

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
            rhinoMaterial.PhysicallyBased.Emission.R,
            rhinoMaterial.PhysicallyBased.Emission.G,
            rhinoMaterial.PhysicallyBased.Emission.B,
        ]

    # Extensions

    extensions = []

    # Opacity => Transmission https://github.com/KhronosGroup/glTF/blob/master/extensions/2.0/Khronos/KHR_materials_transmission/README.md

    transmission = KHR_materials_transmission()

    if opacityTexture is not None and opacityTexture.Enabled:
        # Transmission texture is stored in an images R channel
        # https://github.com/KhronosGroup/glTF/blob/master/extensions/2.0/Khronos/KHR_materials_transmission/README.md#properties
        transmission.TransmissionTexture = GetSingleChannelTexture(
            opacityTexture, RgbaChannel.Red, True
        )
        transmission.TransmissionFactor = GetTextureWeight(opacityTexture)
    else:
        transmission.TransmissionFactor = 1.0 - float(pbr.Opacity)

    extensions.append(transmission)

    # Clearcoat => Clearcoat https://github.com/KhronosGroup/glTF/blob/master/extensions/2.0/Khronos/KHR_materials_clearcoat/README.md

    clearcoat = KHR_materials_clearcoat()

    if clearcoatTexture is not None and clearcoatTexture.Enabled:
        clearcoat.ClearcoatTexture = AddTexture(clearcoatTexture.FileReference.FullPath)
        clearcoat.ClearcoatFactor = GetTextureWeight(clearcoatTexture)
    else:
        clearcoat.ClearcoatFactor = float(pbr.Clearcoat)

    if clearcoatRoughessTexture is not None and clearcoatRoughessTexture.Enabled:
        clearcoat.ClearcoatRoughnessTexture = AddTexture(
            clearcoatRoughessTexture.FileReference.FullPath
        )
        clearcoat.ClearcoatRoughnessFactor = GetTextureWeight(clearcoatRoughessTexture)
    else:
        clearcoat.ClearcoatRoughnessFactor = float(pbr.ClearcoatRoughness)

    if clearcoatNormalTexture is not None and clearcoatNormalTexture.Enabled:
        clearcoat.ClearcoatNormalTexture = AddTextureNormal(clearcoatNormalTexture)

    extensions.append(clearcoat)  # add tag to materials

    # Opacity IOR -> IOR https://github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_materials_ior
    # ior = KHR_materials_ior()
    # Ior = float(pbr.OpacityIOR)
    # material.Extensions.Add(glTFExtensions.KHR_materials_ior.Tag, ior);

    # Specular -> Specular https://github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_materials_specular

    specular = KHR_materials_specular()
    if specularTexture is not None and specularTexture.Enabled:
        # Specular is stored in the textures alpha channel
        specular.SpecularTexture = GetSingleChannelTexture(
            specularTexture, RgbaChannel.Alpha, False
        )
        specular.SpecularFactor = GetTextureWeight(specularTexture)
    else:
        specular.SpecularFactor = float(pbr.Specular)
    extensions.append(specular)

    return gltf_content.add_material(material)


"""
using Rhino.Display;
using Rhino.DocObjects;
using Rhino.Geometry;
using Rhino.Render;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace glTF_BinExporter
{
    enum RgbaChannel
    {
        Red = 0,
        Green = 1,
        Blue = 2,
        Alpha = 3,
    }

    class RhinoMaterialGltfConverter
    {
        public RhinoMaterialGltfConverter(glTFExportOptions options, bool binary, gltfSchemaDummy dummy, List<byte> binaryBuffer, RenderMaterial renderMaterial, LinearWorkflow workflow)
        {
            this.options = options;
            this.binary = binary;
            this.dummy = dummy;
            this.binaryBuffer = binaryBuffer;
            this.rhinoMaterial = renderMaterial.SimulatedMaterial(Rhino.Render.RenderTexture.TextureGeneration.Allow);
            this.renderMaterial = renderMaterial;
            this.workflow = workflow;
        }

        private glTFExportOptions options = null;
        private bool binary = false;
        private gltfSchemaDummy dummy = null;
        private List<byte> binaryBuffer = null;
        private LinearWorkflow workflow = null;

        private Rhino.DocObjects.Material rhinoMaterial = null;
        private RenderMaterial renderMaterial = null;

        

        

        private glTFLoader.Schema.Image GetImageFromFileText(string fileName)
        {
            byte[] imageBytes = GetImageBytesFromFile(fileName);

            var textureBuffer = new glTFLoader.Schema.Buffer()
            {
                Uri = Constants.TextBufferHeader + Convert.ToBase64String(imageBytes),
                ByteLength = imageBytes.Length,
            };

            int textureBufferIdx = dummy.Buffers.AddAndReturnIndex(textureBuffer);

            var textureBufferView = new glTFLoader.Schema.BufferView()
            {
                Buffer = textureBufferIdx,
                ByteOffset = 0,
                ByteLength = textureBuffer.ByteLength,
            };
            int textureBufferViewIdx = dummy.BufferViews.AddAndReturnIndex(textureBufferView);

            return new glTFLoader.Schema.Image()
            {
                BufferView = textureBufferViewIdx,
                MimeType = glTFLoader.Schema.Image.MimeTypeEnum.image_png,
            };
        }

        private glTFLoader.Schema.Image GetImageFromFile(string fileName)
        {
            if (binary)
            {
                return GetImageFromFileBinary(fileName);
            }
            else
            {
                return GetImageFromFileText(fileName);
            }
        }

        private glTFLoader.Schema.Image GetImageFromFileBinary(string fileName)
        {
            byte[] imageBytes = GetImageBytesFromFile(fileName);
            int imageBytesOffset = (int)binaryBuffer.Count;
            binaryBuffer.AddRange(imageBytes);

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

        private byte[] GetImageBytesFromFile(string fileName)
        {
            Bitmap bmp = System.Drawing.Bitmap(fileName);

            return GetImageBytes(bmp);
        }

        

        private glTFLoader.Schema.Image GetImageFromBitmapText(Bitmap bitmap)
        {
            byte[] imageBytes = GetImageBytes(bitmap);

            var textureBuffer = new glTFLoader.Schema.Buffer();

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

            return new glTFLoader.Schema.Image()
            {
                BufferView = textureBufferViewIdx,
                MimeType = glTFLoader.Schema.Image.MimeTypeEnum.image_png,
            };
        }


    }
}
"""
