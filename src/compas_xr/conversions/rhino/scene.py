import sys

sys.path.append(r"C:\Users\rustr\workspace\compas_xr\src")

from compas.geometry import Transformation, Frame

from compas_rhino import unload_modules
from compas_rhino.geometry import RhinoMesh
from compas_rhino.geometry import RhinoCone
from compas_rhino.geometry import RhinoBox
from compas_rhino.geometry import RhinoCylinder
from compas_rhino.geometry import RhinoSphere
from compas_rhino.geometry import RhinoSurface

unload_modules("compas_xr")

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import scriptcontext

from compas_xr.conversions import BaseScene


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


def argsort(seq):  # TODO: upstream to compsa
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)


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


def mesh_from_brep(brep):
    meshes = rg.Mesh.CreateFromBrep(brep)
    guid = rs.JoinMeshes(meshes)
    mesh = rs.coercemesh(guid)
    return RhinoMesh.from_geometry(mesh).to_compas()


def convert_rhino_brep_to_compas(brep, extrusion=None):
    if brep.IsBox:
        if extrusion:
            return RhinoBox.from_geometry(extrusion).to_compas()
        else:
            try:
                return RhinoBox.from_geometry(brep).to_compas()
            except:
                return mesh_from_brep(brep)
    else:
        return mesh_from_brep(brep)
    if brep.IsSolid:
        print("is solid")
    print(brep.HasBrepForm)
    print(brep.IsSurface)


def convert_rhino_object_to_compas(obj):
    if type(obj) == rg.Extrusion:
        brep = rg.Brep.TryConvertBrep(obj)
        if brep:
            return convert_rhino_brep_to_compas(brep, obj)
        else:
            print("extrusion to brep failed")
    elif type(obj) == rg.Brep:
        return convert_rhino_brep_to_compas(obj)
    elif type(obj) == rg.Mesh:
        return RhinoMesh.from_geometry(obj).to_compas()
    else:
        print("%s not covered in export" % type(obj))


def obj_to_scene(obj, scene, parent):

    name = obj.Name
    objgeo = obj.Geometry


    if type(objgeo) == rg.InstanceReferenceGeometry:
        idef = scriptcontext.doc.InstanceDefinitions.FindId(objgeo.ParentIdefId)
        name = idef.Name
        
        # TODO this is not working sometimes
        xf = rs.BlockInstanceXform(obj)
        T = transformation_from_xform(xf)
        Sc, Sh, R, Tl, P = T.decomposed()
        scale_factors = [Sc[0, 0], Sc[1, 1], Sc[2, 2]]
        scale_factors = [abs(v) for v in scale_factors]
        frame = Frame.from_transformation(Tl * R)
        # TODO end

        key, _ = scene.unique_key(name)
        scene.add_layer(key, parent=parent, frame=frame, instance_of=name, scale=scale_factors)

    else:
        element = convert_rhino_object_to_compas(objgeo)
        name = name or "element"
        key, _ = scene.unique_key(name)
        scene.add_layer(key, parent=parent, element=element)


class RhinoScene(BaseScene):
    def __init__(self, name=None):
        from compas_xr.datastructures import Scene

        self.name = name or "RhinoScene"
        self.scene = Scene(name=self.name)
        self.block_names = []
        self.layers = []
        self.materials = []

    @classmethod
    def from_scene(cls, scene):
        """Construct a `RhinoScene` from a :class:`compas_xr.datastructures.Scene`"""
        pass

    def to_compas(self):
        """Convert to a COMPAS object.

        Returns
        -------
        :class:`compas_xr.datastructures.Scene`
            A COMPAS scene.
        """
        scene = Scene()

    @classmethod
    def from_rhino(cls):

        rscene = cls()
        scene = rscene.scene
        block_names = []
        block_depths = []

        # 1. Materials

        # 2. Blocks
        # is this needed to first go through all blocks? maybe make that togehter with everyting else..
        for layer_name in rs.LayerNames():
            parent = rs.ParentLayer(layer_name)
            parent_in_scene = layer_name[(layer_name.rfind(":") + 1) :]
            for guid in rs.ObjectsByLayer(layer_name):
                robj = rs.coercerhinoobject(guid, True)
                if type(robj.Geometry) == rg.InstanceReferenceGeometry:
                    idef = scriptcontext.doc.InstanceDefinitions.FindId(robj.Geometry.ParentIdefId)
                    if idef.Name not in block_names:
                        block_names.append(idef.Name)
                        block_depths.append(0)
                    # go through if we find more instances within
                    names, depths = block_names_within_block(idef)
                    block_names += names
                    block_depths += depths

        if len(block_names):
            # sort based on block depths
            idxs = argsort(block_depths)
            block_depths = [block_depths[i] for i in idxs]
            block_names = [block_names[i] for i in idxs]
            print(block_names)
            
            # add to scene
            references = scene.add_layer("references")
            for block_name in reversed(block_names):  # start with the one that has the least depth
                idef = scriptcontext.doc.InstanceDefinitions.Find(block_name)
                block_key = scene.unique_key(block_name)
                scene.add_layer(block_key, parent="references")
                for obj in idef.GetObjects():
                    obj_to_scene(obj, scene, block_key)

        # 3. Other objects
        for layer_name in rs.LayerNames():  # this is ordered
            parent = rs.ParentLayer(layer_name)
            parent_in_scene = layer_name[(layer_name.rfind(":") + 1) :]
            key = scene.unique_key(parent_in_scene)
            scene.add_layer(key, parent=parent)
            for guid in rs.ObjectsByLayer(layer_name):
                robj = rs.coercerhinoobject(guid, True)
                obj_to_scene(robj, scene, key)

        # remove orphans
        return rscene


if __name__ == "__main__":

    rhino_scene = RhinoScene.from_rhino()
