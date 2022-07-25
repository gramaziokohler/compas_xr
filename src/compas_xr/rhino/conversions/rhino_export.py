import sys
import os
import Rhino
import scriptcontext
import rhinoscriptsyntax as rs

from compas_rhino import unload_modules

unload_modules("compas")

from compas_rhino.conversions import xform_to_rhino
from compas_rhino.conversions import RhinoMesh
from compas.files.gltf.gltf import GLTF
from compas.files.gltf import GLTFContent
from compas.files.gltf.data_classes import PBRMetallicRoughnessData
from compas.files.gltf.data_classes import MaterialData
from compas.utilities import color_to_rgb
from compas.geometry import Frame, Transformation
import compas


sys.path.append(r"C:\Users\rustr\workspace\compas_xr\src")
from compas_xr.rhino.conversions.rhino_material import AddMaterial


# https://github.com/Stykka/glTF-Bin/blob/master/glTF-BinExporter/RhinoDocGltfConverter.cs


def ExplodeRecursive(instanceObject, instanceTransform, pieces, transforms):
    for i in range(instanceObject.InstanceDefinition.ObjectCount):
        rhinoObject = instanceObject.InstanceDefinition.Object(i)
        if type(rhinoObject) == Rhino.Geometry.InstanceReferenceGeometry:
            nestedObject = scriptcontext.doc.InstanceDefinitions.FindId(rhinoObject.ParentIdefId)
            nestedTransform = instanceTransform * nestedObject.InstanceXform
            ExplodeRecursive(nestedObject, nestedTransform, pieces, transforms)
        else:
            pieces.append(rhinoObject)
            transforms.append(instanceTransform)


def GetObjectMaterial(rhinoObject):
    source = rhinoObject.Attributes.MaterialSource
    renderMaterial = None
    if source == Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject:
        renderMaterial = rhinoObject.RenderMaterial
    elif source == Rhino.DocObjects.ObjectMaterialSource.MaterialFromLayer:
        layerIndex = rhinoObject.Attributes.LayerIndex
        renderMaterial = GetLayerMaterial(layerIndex)
    return renderMaterial


def GetLayerMaterial(layerIndex):
    if layerIndex < 0 or layerIndex >= scriptcontext.doc.Layers.Count:
        return None
    else:
        return scriptcontext.doc.Layers[layerIndex].RenderMaterial


def MeshIsValidForExport(mesh):
    if mesh is None:
        return False
    if mesh.Vertices.Count == 0:
        return False
    if mesh.Faces.Count == 0:
        return False
    if options.ExportOpenMeshes is False and mesh.IsClosed is False:
        return False
    return True


def DefaultMaterial():
    return Rhino.DocObjects.Material.DefaultMaterial.RenderMaterial


def GetObjectName(rhinoObject):
    return rhinoObject.Name if rhinoObject.Name else ""


def GetMaterial(material, rhinoObject, options, gltf_content, materialsMap):
    print("material", material)
    if not options.ExportMaterials:
        return False
    if material is None and options.UseDisplayColorForUnsetMaterials:
        objectColor = GetObjectColor(rhinoObject)
        return CreateSolidColorMaterial(objectColor, gltf_content)
    elif material is None:
        material = DefaultMaterial()
    materialId = material.Id

    if materialId not in materialsMap:
        materialIndex = AddMaterial(gltf_content, material)
        materialsMap[materialId] = materialIndex
    else:
        materialIndex = materialsMap[materialId]

    return materialIndex


def CreateSolidColorMaterial(color, gltf_content):
    r, g, b = color_to_rgb((color.R, color.G, color.B), normalize=True)
    a, _, _ = color_to_rgb((color.A, 0, 0), normalize=True)
    material = MaterialData()
    material.pbr_metallic_roughness = PBRMetallicRoughnessData()
    material.pbr_metallic_roughness.base_color_factor = [r, g, b, a]
    return gltf_content.add_material(material)  # return key?


def GetObjectColor(rhinoObject):
    if rhinoObject.Attributes.ColorSource == Rhino.DocObjects.ObjectColorSource.ColorFromLayer:
        layerIndex = rhinoObject.Attributes.LayerIndex
        return rhinoObject.Document.Layers[layerIndex].Color  # convert to float?
    else:
        return rhinoObject.Attributes.ObjectColor  # convert to float?


def SanitizeRhinoObjects(rhinoObjects, options):
    explodedObjects = []

    object_export_data = {
        "Meshes": None,
        "Transform": None,
        "RenderMaterial": None,
        "Object": None,
    }

    for rhinoObject in rhinoObjects:

        rhinoObject = rs.coercerhinoobject(rhinoObject, True)

        if type(rhinoObject) == Rhino.Geometry.InstanceReferenceGeometry:
            pieces, transforms = [], []
            instanceObject = scriptcontext.doc.InstanceDefinitions.FindId(rhinoObject.ParentIdefId)
            ExplodeRecursive(instanceObject, Rhino.Geometry.Transform.Identity, pieces, transforms)
            for item, trans in zip(pieces, transforms):
                data = object_export_data.copy()
                data["Object"] = item
                data["Transform"] = trans
                data["RenderMaterial"] = GetObjectMaterial(item)
                explodedObjects.append(data)

        else:
            data = object_export_data.copy()
            data["Object"] = rhinoObject
            data["Transform"] = Rhino.Geometry.Transform.Identity
            data["RenderMaterial"] = GetObjectMaterial(rhinoObject)
            explodedObjects.append(data)

    sanitized_objects = []

    for data in explodedObjects:

        item = data["Object"]
        trans = data["Transform"]

        # Remove Unmeshable
        if not item.IsMeshable(Rhino.Geometry.MeshType.Any):
            continue

        if type(item) is Rhino.Geometry.SubD:

            subd = item

            level = options.SubDLevel
            mesh = Rhino.Geometry.Mesh.CreateFromSubD(subd, level)
            mesh.Transform(trans)  # item.Transform
            item.Meshes = Rhino.Geometry.Mesh(mesh)
        else:
            parameters = item.GetRenderMeshParameters()
            if item.MeshCount(Rhino.Geometry.MeshType.Render, parameters) == 0:
                item.CreateMeshes(Rhino.Geometry.MeshType.Render, parameters, False)

            meshes = []

            for mesh in item.GetMeshes(Rhino.Geometry.MeshType.Render):
                mesh.EnsurePrivateCopy()
                mesh.Transform(trans)  # item.Transform
                # Remove bad meshes
                if MeshIsValidForExport(mesh):
                    meshes.append(mesh)

            data["Meshes"] = meshes

        if len(data["Meshes"]):
            sanitized_objects.append(data)

    return sanitized_objects


class glTFExportOptions:
    ExportLayers = True
    ExportOpenMeshes = True
    SubDLevel = True
    ExportMaterials = True
    UseDisplayColorForUnsetMaterials = False
    ExportVertexNormals = True
    ExportTextureCoordinates = True
    ExportVertexColors = True
    MapRhinoZToGltfY = True
    UseDracoCompression = False  # TODO


objects = rs.AllObjects()
options = glTFExportOptions()

sanitized = SanitizeRhinoObjects(objects, options)

gltf_content = GLTFContent()
materialsMap = {}

scene = gltf_content.add_scene()

worldZX = Frame((0, 0, 0), (1, 0, 0), (0, 0, -1))
ZtoYUp = Transformation.from_frame_to_frame(Frame.worldXY(), worldZX)
ZtoYUp = xform_to_rhino(ZtoYUp)

for k, data in enumerate(sanitized):

    # if k < 318:
    #    continue

    # adds material to the content
    materialIndex = GetMaterial(data["RenderMaterial"], data["Object"], options, gltf_content, materialsMap)

    print(gltf_content.materials)

    for i, rhino_mesh in enumerate(data["Meshes"]):
        print("rhino_mesh", rhino_mesh)
        node_name = "%04d_%s_%04d" % (k, GetObjectName(data["Object"]), i)

        print(node_name)
        node = scene.add_child(node_name=node_name)

        # pre process mesh etc..
        ok = rhino_mesh.Faces.ConvertQuadsToTriangles()

        if options.MapRhinoZToGltfY:
            rhino_mesh.Transform(ZtoYUp)
            rhino_mesh.TextureCoordinates.ReverseTextureCoordinates(1)

        mesh = RhinoMesh.from_geometry(rhino_mesh).to_compas()
        # mesh.quads_to_triangles()
        mesh_data = node.add_mesh(mesh)  # one mesh per node?
        pd = mesh_data.primitive_data_list[0]  # only one
        pd.material = materialIndex

        # normals = [mesh.vertex_normal(k) for k in mesh.vertices()]

        if rhino_mesh.Normals.Count > 0 and options.ExportVertexNormals:
            pd.attributes["NORMAL"] = [(float(v.X), float(v.Y), float(v.Z)) for v in rhino_mesh.Normals]

        if rhino_mesh.TextureCoordinates.Count > 0 and options.ExportTextureCoordinates:
            pd.attributes["TEXCOORD_0"] = [(float(u), float(v)) for u, v in rhino_mesh.TextureCoordinates]

        if rhino_mesh.VertexColors.Count > 0 and options.ExportVertexColors:
            colors = []
            for color in rhino_mesh.VertexColors:
                r, g, b = color_to_rgb((color.R, color.G, color.B), normalize=True)
                a, _, _ = color_to_rgb((color.A, 0, 0), normalize=True)
                colors.append([r, g, b, a])
            # pd.attributes["COLOR_0"] = colors


gltf_filepath = os.path.join(compas.APPDATA, "data", "gltfs", "rhino_export.gltf")
print(gltf_filepath)
gltf = GLTF(gltf_filepath)
gltf.content = gltf_content
gltf.export(embed_data=False)
