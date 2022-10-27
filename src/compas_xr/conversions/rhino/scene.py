import compas
from compas.geometry import Frame  # noqa E402
from compas.geometry import Transformation  # noqa E402

if compas.IPY:
    import Rhino
    import rhinoscriptsyntax as rs  # noqa E402
    import Rhino.Geometry as rg  # noqa E402
    import scriptcontext  # noqa E402
    from compas_rhino import unload_modules  # noqa E402
    from compas_rhino.geometry import RhinoMesh  # noqa E402
    from compas_rhino.geometry import RhinoBox  # noqa E402
    from compas.utilities import color_to_rgb  # noqa E402

from compas_xr.conversions import BaseScene  # noqa E402
from compas_xr.conversions.rhino.material import RhinoMaterial  # noqa E402

from compas_xr.datastructures import Material  # noqa E402
from compas_xr.datastructures import PBRMetallicRoughness  # noqa E402


def transformation_from_xform(xform):  # TODO upstream to compas
    """Creates a :class:`Transformation` from a Rhino Transform instance.

    Parameters
    ----------
    xform (:class:`Rhino.Geometry.Transform`):
        RhinoCommon Transform object

    Returns
    -------
    :class:`Transformation`
        Compas transformation object
    """
    transformation = Transformation()
    for i in range(0, 4):
        for j in range(0, 4):
            transformation[i, j] = xform[i, j]
    return transformation


def block_names_within_block(idef, depth=0):
    def recursive(idef, depth, block_names, block_depths):
        for obj in idef.GetObjects():
            if type(obj.Geometry) == rg.InstanceReferenceGeometry:
                name = obj.InstanceDefinition.Name
                if name not in block_names:
                    block_names.append(name)
                    block_depths.append(depth + 1)
                recursive(obj.InstanceDefinition, depth + 1, block_names, block_depths)

    block_names = []
    block_depths = []
    recursive(idef, depth, block_names, block_depths)
    return block_names, block_depths


def mesh_from_brep(brep, obj):
    parameters = obj.GetRenderMeshParameters()
    if obj.MeshCount(Rhino.Geometry.MeshType.Render, parameters) == 0:
        obj.CreateMeshes(Rhino.Geometry.MeshType.Render, parameters, False)

    meshes = []
    for rmesh in obj.GetMeshes(Rhino.Geometry.MeshType.Render):
        rmesh.EnsurePrivateCopy()
        if rmesh is not None and rmesh.Vertices.Count > 0 and rmesh.Faces.Count > 0:
            cmesh = RhinoMesh.from_geometry(rmesh).to_compas()
            if rmesh.TextureCoordinates.Count > 0:
                texture_coordinates = [(float(u), float(v)) for u, v in rmesh.TextureCoordinates]
                for k, v in zip(cmesh.vertices(), texture_coordinates):
                    cmesh.vertex_attribute(k, "texture_coordinate", value=v)

            if rmesh.Normals.Count > 0:
                normals = [(float(v.X), float(v.Y), float(v.Z)) for v in rmesh.Normals]
                for k, v in zip(cmesh.vertices(), normals):
                    cmesh.vertex_attribute(k, "vertex_normal", value=v)
            if rmesh.VertexColors.Count > 0:
                colors = []
                for color in rmesh.VertexColors:
                    r, g, b = color_to_rgb((color.R, color.G, color.B), normalize=True)
                    a, _, _ = color_to_rgb((color.A, 0, 0), normalize=True)
                    colors.append([r, g, b, a])
                for k, v in zip(cmesh.vertices(), colors):
                    cmesh.vertex_attribute(k, "vertex_color", value=v)
            meshes.append(cmesh)
    return meshes


def convert_rhino_brep_to_compas(brep, extrusion=None, robj=None):
    if brep.IsBox:
        if extrusion:
            return RhinoBox.from_geometry(extrusion).to_compas()
        else:
            try:
                return RhinoBox.from_geometry(brep).to_compas()
            except:  # noqa E722
                return mesh_from_brep(brep, robj)
    else:
        return mesh_from_brep(brep)


def convert_rhino_object_to_compas(obj, robj=None):
    if type(obj) == rg.Extrusion:
        brep = rg.Brep.TryConvertBrep(obj)
        if brep:
            return convert_rhino_brep_to_compas(brep, obj, robj=robj)
        else:
            print("extrusion to brep failed")
    elif type(obj) == rg.Brep:
        return convert_rhino_brep_to_compas(obj, robj=robj)
    elif type(obj) == rg.Mesh:
        return RhinoMesh.from_geometry(obj).to_compas()
    else:
        print("%s not covered in export" % type(obj))


def obj_to_scene(obj, scene, parent):

    name = obj.Name
    objgeo = obj.Geometry

    material = RhinoMaterial.from_object(obj)

    if material.material is None:
        color_rgba = RhinoMaterial.color_from_object(obj)
        matname = RhinoMaterial.name_from_color(color_rgba)
        if matname not in scene.material_names:
            print(matname)
            c_material = Material(name=matname)
            c_material.pbr_metallic_roughness = PBRMetallicRoughness()
            c_material.pbr_metallic_roughness.base_color_factor = color_rgba
            c_material.pbr_metallic_roughness.metallic_factor = 0.0
            mat_key = scene.add_material(c_material)
        else:
            mat_key = scene.material_index_by_name(matname)
        # add defaults
    else:
        c_material = material.to_compas()
        if c_material.name not in scene.material_names:
            print(c_material.name)
            mat_key = scene.add_material(c_material)
        else:
            mat_key = scene.material_index_by_name(c_material.name)

    if type(objgeo) == rg.InstanceReferenceGeometry:
        idef = scriptcontext.doc.InstanceDefinitions.FindId(objgeo.ParentIdefId)
        name = idef.Name

        # check if the reference to the instance already exists.
        # if not, add to scene
        if not scene.has_layer("references"):
            scene.add_layer("references")

        if not scene.has_layer(name):
            # add the reference to the scene
            scene.add_layer(name, parent="references", is_reference=True)  # here we assume the name to be unique
            for robj in idef.GetObjects():
                obj_to_scene(robj, scene, name)
        else:
            # it already exists, we dont have to add it
            pass

        # add the instance to the scene

        # TODO this is not working sometimes
        xf = rs.BlockInstanceXform(obj)
        T = transformation_from_xform(xf)
        Sc, Sh, R, Tl, P = T.decomposed()
        scale_factors = [Sc[0, 0], Sc[1, 1], Sc[2, 2]]
        scale_factors = [abs(v) for v in scale_factors]
        frame = Frame.from_transformation(Tl * R)
        # TODO end

        key = scene.unique_key(name)
        # print("parent", parent)
        scene.add_layer(key, parent=parent, frame=frame, instance_of=name, scale=scale_factors)  # , material=mat_key) # material?

    else:

        element = convert_rhino_object_to_compas(objgeo, obj)

        if isinstance(element, list):
            for i, elem in enumerate(element):
                name = name or "element"
                key = scene.unique_key(name)

                texture_coordinates = elem.vertices_attribute("texture_coordinate")
                print("texture_coordinates", texture_coordinates[0])

                scene.add_layer(key, parent=parent, element=elem, material=mat_key)

        else:
            name = name or "element"
            key = scene.unique_key(name)
            # print("parent", parent)
            scene.add_layer(key, parent=parent, element=element, material=mat_key)


class RhinoScene(BaseScene):
    def __init__(self):

        super(RhinoScene, self).__init__(name="RhinoScene")

        self.block_names = []
        self.layers = []
        self.materials = []

    @classmethod
    def from_scene(cls, scene):
        """Construct a `RhinoScene` from a :class:`compas_xr.datastructures.Scene`"""
        raise NotImplementedError

    @classmethod
    def from_rhino(cls):

        rscene = cls()
        scene = rscene.scene

        for layer_name in rs.LayerNames():  # this is ordered
            parent = rs.ParentLayer(layer_name)
            if parent is not None:
                parent = parent[(parent.rfind(":") + 1) :]  # noqa E203
                parent = parent.replace(" ", "_")
            parent_in_scene = layer_name[(layer_name.rfind(":") + 1) :]  # noqa E203
            parent_in_scene = parent_in_scene.replace(" ", "_")

            key = scene.unique_key(parent_in_scene)
            scene.add_layer(key, parent=parent)

            for guid in rs.ObjectsByLayer(layer_name):
                robj = rs.coercerhinoobject(guid, True)
                obj_to_scene(robj, scene, key)  # takes care of the references, instances, materials

        # remove orphans
        return rscene


if __name__ == "__main__":
    import os
    from compas_xr import DATA

    rhino_scene = RhinoScene.from_rhino()
    scene = rhino_scene.to_compas()
    filename = os.path.join(DATA, "ball.json")
    print(scene.data)
    scene.to_json(filename, pretty=True)
    # filename = os.path.join(DATA, "rhinoscene.json")
    # scene = Scene.from_json(filename)
    # scene.to_gltf(os.path.join(DATA, "ball.gltf"))
