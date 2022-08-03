import os
from pxr import Sdf
from pxr import Usd
from pxr import UsdGeom
from pxr import UsdShade

from compas.geometry import Box
from compas.geometry import Cylinder
from compas.geometry import Transformation
from compas.geometry import Scale
from compas.datastructures import Mesh

from compas_usd.conversions import prim_from_box
from compas_usd.conversions import prim_from_mesh
from compas_usd.conversions import prim_default
from compas_usd.conversions import prim_from_cylinder
from compas_usd.conversions import frame_and_scale_from_prim
from compas_usd.conversions import box_from_prim
from compas_usd.material import USDMaterial

from compas_xr.conversions import BaseScene


class USDScene(BaseScene):
    """Wrapper about Usd.Stage."""

    def __init__(self, scene=None):
        self.scene = scene

    @classmethod
    def from_usd(cls, filename):
        scene = cls()
        scene.scene = Usd.Stage.Open(filename)
        return scene

    def reference_filename(self, reference_name, filepath=None, fullpath=True, extension=None):
        stage = self.scene
        filepath = filepath or str(stage.GetRootLayer().resolvedPath)  # .realPath
        if not extension:
            _, extension = os.path.splitext(filepath)
        filename = "%s%s" % (reference_name, extension)
        if fullpath:
            return os.path.join(os.path.dirname(filepath), filename)
        else:
            return filename

    def prim_instance(self, path, reference_name, filepath=None, xform=False, extension=None):
        stage = self.scene
        reference_filepath = self.reference_filename(reference_name, filepath=filepath, fullpath=False, extension=extension)
        print(reference_filepath)
        if not xform:
            ref = stage.OverridePrim(path)
            ref.GetReferences().AddReference("./%s" % reference_filepath)
        else:
            ref = UsdGeom.Xform.Define(stage, path)
            ref.GetPrim().GetReferences().AddReference("./%s" % reference_filepath)

        ref_xform = UsdGeom.Xformable(ref)
        ref_xform.SetXformOpOrder([])
        return ref

    @classmethod
    def from_scene(cls, scene, filepath=None):

        if scene.has_references and filepath is None:
            raise ValueError("Please pass a filename for a scene with references")

        usd_scene = cls()
        if filepath:
            usd_scene.scene = Usd.Stage.CreateNew(filepath)
        else:
            usd_scene.scene = Usd.Stage.CreateInMemory()
        stage = usd_scene.scene

        UsdGeom.SetStageUpAxis(stage, scene.up_axis)  # UsdGeom.Tokens.z

        image_uris = [image.uri for image in scene.images]
        usd_materials = []
        for material in scene.materials:
            usd_materials.append(USDMaterial.from_material(stage, material, image_uris=image_uris, textures=scene.textures))

        # Export the references first, otherwise we will not find a linkage
        visited = []
        for key in scene.ordered_references:
            subscene = scene.subscene(key)
            children = scene._all_children(key, include_key=True)
            visited += children
            reference_filepath = usd_scene.reference_filename(key, fullpath=True)
            USDScene.from_scene(subscene, filepath=reference_filepath)  # .to_usd
            # reference_filepath = usd_scene.reference_filename(key, fullpath=True)
            # subscene.to_usd(reference_filepath)

        print(visited)

        for key in scene.ordered_keys:
            if key in visited:
                continue
            parent = scene.node_attribute(key, "parent")
            is_reference = scene.node_attribute(key, "is_reference")
            frame = scene.node_attribute(key, "frame")
            element = scene.node_attribute(key, "element")
            instance_of = scene.node_attribute(key, "instance_of")
            scale = scene.node_attribute(key, "scale")

            if instance_of:
                print("instance_of", instance_of)

            tex_coords = scene.node_attribute(key, "tex_coords")

            mkey = scene.node_attribute(key, "material")

            transformation = Transformation.from_frame(frame) if frame else Transformation()
            if scale:
                transformation = transformation * Scale.from_factors(scale)

            is_root = True if not parent else False
            path = "/" + "/".join(reversed(scene.node_to_root(key)))

            if not is_reference:
                # if there is a frame in the node, we first have to add Xform

                if instance_of:
                    if frame:
                        prim_default(stage, path, transformation)
                        path += "/element"

                    # GetRealPath() is string
                    prim = usd_scene.prim_instance(path, scene.node_attribute(key, "instance_of"), filepath=str(stage.GetRootLayer().resolvedPath))

                else:

                    if frame:
                        prim = prim_default(stage, path, transformation)
                        path += "/element"

                    if element:
                        if type(element) == Box:
                            prim = prim_from_box(stage, path, element)
                        elif type(element) == Mesh:
                            prim = prim_from_mesh(stage, path, element)
                            if tex_coords:
                                usd_tex_coords = prim.CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.varying)
                                usd_tex_coords.Set(tex_coords)

                        elif type(element) == Cylinder:
                            prim = prim_from_cylinder(stage, path, element)
                        else:
                            print(type(element))
                            raise NotImplementedError

                    if not frame and not element:
                        prim = prim_default(stage, path, transformation)
            else:
                raise ValueError("we should never come here")

            if mkey is not None:
                UsdShade.MaterialBindingAPI(prim).Bind(usd_materials[mkey].material)

            if is_root and key != "references":
                stage.SetDefaultPrim(prim.GetPrim())  # dont use references as default layer

        print("stage.GetRootLayer()", type(stage.GetRootLayer()))
        stage.GetRootLayer().Save()
        # stage.Export(filepath) # removes the linkages

        return usd_scene

    def to_compas(self):
        from compas_xr.datastructures import Scene

        stage = self.scene
        scene = Scene(name="usd_scene", up_axis=UsdGeom.GetStageUpAxis(stage))

        keys, names, parents, frames, scales, elements, materials = [], {}, {}, {}, {}, {}, {}
        material_paths = []

        for i, obj in enumerate(stage.TraverseAll()):  # Traverse()

            typename = obj.GetTypeName()
            if typename in ["Scope", "Material", "Shader"]:  # handled in materials
                continue

            path = str(obj.GetPath())
            node_names = path.split("/")[1:]

            keys.append(i)
            names[i] = node_names[-1]
            if len(node_names) > 1:
                parents[i] = node_names[-2]

            if obj.IsInstance():
                raise NotImplementedError

            if typename == "Xform":
                frame, scale = frame_and_scale_from_prim(obj)
                frames[i] = frame
                scales[i] = scale

            elif typename == "Cube":
                elements[i] = box_from_prim(obj)

            else:
                raise NotImplementedError

            if "material:binding" in obj.GetPropertyNames():
                material_path = str(obj.GetRelationship("material:binding").GetTargets()[0])
                if material_path not in material_paths:
                    material_paths.append(material_path)
                materials[i] = material_paths.index(material_path)

        for key in keys:
            name = names.get(key, None)
            parent = parents.get(key, None)
            material = materials.get(key, None)
            element = elements.get(key, None)
            frame = frames.get(key, None)
            # is_reference ?
            # instance_of ?
            print(name, parent, frame, element, material)
            scene.add_layer(name, parent=parent, frame=frame, element=element, material=material)

        materials = []
        for path in material_paths:
            material = USDMaterial.from_path(stage, path).to_compas()
            materials.append(material)

        return scene

    def to_usd(self, filename):
        """
        for key, subscene in self.subscenes.items():
            reference_filepath = self.reference_filename(key, filepath=filename, fullpath=True)
            print(reference_filepath)
            subscene.to_usd(reference_filepath)
        """
        # self.scene.Export(filename)
        # self.scene.GetRootLayer().Save()
        pass
