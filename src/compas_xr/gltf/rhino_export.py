import Rhino
import System
import scriptcontext
import rhinoscriptsyntax as rs

from compas.utilities import color_to_rgb
from compas.files.gltf.data_classes import MaterialData
from compas.files.gltf.data_classes import PBRMetallicRoughnessData
from compas.files.gltf import GLTFContent

import sys

from compas_rhino import unload_modules

unload_modules("compas_xr")

sys.path.append(r"C:\Users\rustr\workspace\compas_xr\src")

from compas_xr.gltf.rhino_material import AddMaterial

# https://github.com/Stykka/glTF-Bin/blob/master/glTF-BinExporter/RhinoDocGltfConverter.cs


def ExplodeRecursive(instanceObject, instanceTransform, pieces, transforms):
    for i in range(instanceObject.InstanceDefinition.ObjectCount):
        rhinoObject = instanceObject.InstanceDefinition.Object(i)
        if type(rhinoObject) == Rhino.Geometry.InstanceReferenceGeometry:
            nestedObject = scriptcontext.doc.InstanceDefinitions.FindId(
                rhinoObject.ParentIdefId
            )
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
    if mesh == None:
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
    if material == None and options.UseDisplayColorForUnsetMaterials:
        objectColor = GetObjectColor(rhinoObject)
        return CreateSolidColorMaterial(objectColor, gltf_content)
    elif material == None:
        material = DefaultMaterial()
    materialId = material.Id

    if materialId not in materialsMap:
        # materialConverter = RhinoMaterialGltfConverter(
        #    options, binary, dummy, binaryBuffer, material, workflow
        # )

        materialIndex = AddMaterial(gltf_content, material)
        # materialIndex = materialConverter.AddMaterial()
        materialsMap[materialId] = materialIndex

    return materialIndex


def CreateSolidColorMaterial(color, gltf_content):
    r, g, b = color_to_rgb((color.R, color.G, color.B), normalize=True)
    a, _, _ = color_to_rgb((color.A, 0, 0), normalize=True)
    material = MaterialData()
    material.pbr_metallic_roughness = PBRMetallicRoughnessData()
    material.pbr_metallic_roughness.base_color_factor = [r, g, b, a]
    return gltf_content.add_material(material)  # return key?


def GetObjectColor(rhinoObject):
    if (
        rhinoObject.Attributes.ColorSource
        == Rhino.DocObjects.ObjectColorSource.ColorFromLayer
    ):
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
            instanceObject = scriptcontext.doc.InstanceDefinitions.FindId(
                rhinoObject.ParentIdefId
            )
            ExplodeRecursive(
                instanceObject, Rhino.Geometry.Transform.Identity, pieces, transforms
            )
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

                if options.SubDExportMode == SubDMode.ControlNet:
                    mesh = Rhino.Geometry.Mesh.CreateFromSubDControlNet(subd)
                    mesh.Transform(trans)  # item.Transform
                    item.Meshes = Rhino.Geometry.Mesh(mesh)
                else:
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


"""
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Rhino.DocObjects;
using Rhino;
using glTFLoader.Schema;
using Rhino.Render;
using Rhino.Display;

namespace glTF_BinExporter
{
    public class ObjectExportData
    {
        public Rhino.Geometry.Mesh[] Meshes = null;
        public Rhino.Geometry.Transform Transform = Rhino.Geometry.Transform.Identity;
        public RenderMaterial RenderMaterial = null;
        public RhinoObject Object = null;
    }

    class RhinoDocGltfConverter
    {
        public RhinoDocGltfConverter(glTFExportOptions options, bool binary, RhinoDoc doc, IEnumerable<RhinoObject> objects, LinearWorkflow workflow)
        {
            this.doc = doc;
            this.options = options;
            this.binary = binary;
            this.objects = objects;
            this.workflow = workflow;
        }

        public RhinoDocGltfConverter(glTFExportOptions options, bool binary, RhinoDoc doc, LinearWorkflow workflow)
        {
            this.doc = doc;
            this.options = options;
            this.binary = binary;
            this.objects = doc.Objects;
            this.workflow = null;
        }

        private RhinoDoc doc = null;

        private IEnumerable<RhinoObject> objects = null;

        private bool binary = false;
        private glTFExportOptions options = null;
        private LinearWorkflow workflow = null;

        private Dictionary<Guid, int> materialsMap = new Dictionary<Guid, int>();

        private gltfSchemaDummy dummy = new gltfSchemaDummy();

        private List<byte> binaryBuffer = new List<byte>();

        private Dictionary<int, Node> layers = new Dictionary<int, Node>();

        private RenderMaterial defaultMaterial = null;
        private RenderMaterial DefaultMaterial
        {
            get
            {
                if(defaultMaterial == null)
                {
                    defaultMaterial = Rhino.DocObjects.Material.DefaultMaterial.RenderMaterial;
                }

                return defaultMaterial;
            }
        }
        public Gltf ConvertToGltf()
        {
            dummy.Scene = 0;
            dummy.Scenes.Add(new gltfSchemaSceneDummy());

            dummy.Asset = new Asset()
            {
                Version = "2.0",
            };

            dummy.Samplers.Add(new Sampler()
            {
                MinFilter = Sampler.MinFilterEnum.LINEAR,
                MagFilter = Sampler.MagFilterEnum.LINEAR,
                WrapS = Sampler.WrapSEnum.REPEAT,
                WrapT = Sampler.WrapTEnum.REPEAT,
            });

            if(options.UseDracoCompression)
            {
                dummy.ExtensionsUsed.Add(glTFExtensions.KHR_draco_mesh_compression.Tag);
                dummy.ExtensionsRequired.Add(glTFExtensions.KHR_draco_mesh_compression.Tag);
            }

            dummy.ExtensionsUsed.Add(glTFExtensions.KHR_materials_transmission.Tag);
            dummy.ExtensionsUsed.Add(glTFExtensions.KHR_materials_clearcoat.Tag);
            dummy.ExtensionsUsed.Add(glTFExtensions.KHR_materials_ior.Tag);
            dummy.ExtensionsUsed.Add(glTFExtensions.KHR_materials_specular.Tag);

            var sanitized = SanitizeRhinoObjects(objects);

            foreach(ObjectExportData exportData in sanitized)
            {
                int? materialIndex = GetMaterial(exportData.RenderMaterial, exportData.Object);

                RhinoMeshGltfConverter meshConverter = new RhinoMeshGltfConverter(exportData, materialIndex, options, binary, dummy, binaryBuffer);
                int meshIndex = meshConverter.AddMesh();

                glTFLoader.Schema.Node node = new glTFLoader.Schema.Node()
                {
                    Mesh = meshIndex,
                    Name = GetObjectName(exportData.Object),
                };

                int nodeIndex = dummy.Nodes.AddAndReturnIndex(node);

                if(options.ExportLayers)
                {
                    AddToLayer(doc.Layers[exportData.Object.Attributes.LayerIndex], nodeIndex);
                }
                else
                {
                    dummy.Scenes[dummy.Scene].Nodes.Add(nodeIndex);
                }
            }

            if (binary && binaryBuffer.Count > 0)
            {
                //have to add the empty buffer for the binary file header
                dummy.Buffers.Add(new glTFLoader.Schema.Buffer()
                {
                    ByteLength = (int)binaryBuffer.Count,
                    Uri = null,
                });
            }

            return dummy.ToSchemaGltf();
        }

        private void AddToLayer(Layer layer, int child)
        {
            if(layers.TryGetValue(layer.Index, out Node node))
            {
                if (node.Children == null)
                {
                    node.Children = new int[1] { child };
                }
                else
                {
                    node.Children = node.Children.Append(child).ToArray();
                }
            }
            else
            {
                node = new Node()
                {
                    Name = layer.Name,
                    Children = new int[1] { child },
                };
                
                layers.Add(layer.Index, node);

                int nodeIndex = dummy.Nodes.AddAndReturnIndex(node);

                Layer parentLayer = doc.Layers.FindId(layer.ParentLayerId);

                if (parentLayer == null)
                {
                    dummy.Scenes[dummy.Scene].Nodes.Add(nodeIndex);
                }
                else
                {
                    AddToLayer(parentLayer, nodeIndex);
                }
            }
        }

        

        public byte[] GetBinaryBuffer()
        {
            return binaryBuffer.ToArray();
        }

        

    }
}
"""


class glTFExportOptions:
    ExportLayers = True
    SubDExportMode = False
    ExportOpenMeshes = True
    SubDLevel = True
    ExportMaterials = True
    UseDisplayColorForUnsetMaterials = True


objects = rs.AllObjects()


options = glTFExportOptions()

sanitized = SanitizeRhinoObjects(objects, options)

gltf_content = GLTFContent()
materialsMap = {}

print(sanitized)

for data in sanitized:

    print(data)

    materialIndex = GetMaterial(
        data["RenderMaterial"], data["Object"], options, gltf_content, materialsMap
    )

    content = GLTFContent()
    scene = content.add_scene()

    meshConverter = RhinoMeshGltfConverter(
        exportData, materialIndex, options, binary, dummy, binaryBuffer
    )
    meshIndex = meshConverter.AddMesh()

    node = scene.add_child(node_name=GetObjectName(exportData.Object))
    mesh_data = node.add_mesh(mesh)

    if options.ExportLayers:
        AddToLayer(doc.Layers[exportData.Object.Attributes.LayerIndex], nodeIndex)
    else:
        # dummy.Scenes[dummy.Scene].Nodes.Add(nodeIndex)
        pass
