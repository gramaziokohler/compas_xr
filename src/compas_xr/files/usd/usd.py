"""
TODO: This file should be removed and contents migrated to compas_usd
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from pxr import UsdGeom
from compas_nurbs.utilities import unflatten
from compas.utilities import flatten
from compas.geometry import transpose_matrix
from compas.geometry import Rotation


def prim_from_surface(stage, path, surface):
    """Returns a ``pxr.UsdGeom.NurbsPatch``

    control_points = [[[0, 0, 0], [0, 4, 0], [0, 8, -3]], [[2, 0, 6], [2, 4, 0], [2, 8, 0]], [[4, 0, 0], [4, 4, 0], [4, 8, 3]], [[6, 0, 0], [6, 4, -3], [6, 8, 0]]]
    degree = (3, 2)
    surface = Surface(control_points, degree)
    prim_from_surface(stage, "/surface", surface)
    UsdGeom.NurbsPatch(Usd.Prim(</surface>))
    """
    degree_u, degree_v = surface.degree
    knot_vector_u, knot_vector_v = surface.knot_vector
    count_u, count_v = surface.count

    # upside down
    weights = list(flatten(surface.weights))
    weights = list(flatten(transpose_matrix(unflatten(weights, count_v))))
    points = list(flatten(surface.control_points))
    points = list(flatten(transpose_matrix(unflatten(points, count_v))))

    prim = UsdGeom.NurbsPatch.Define(stage, path)
    prim.CreateUVertexCountAttr(count_u)
    prim.CreateVVertexCountAttr(count_v)
    prim.CreateUOrderAttr(degree_u + 1)
    prim.CreateVOrderAttr(degree_v + 1)
    prim.CreateUKnotsAttr(knot_vector_u)
    prim.CreateVKnotsAttr(knot_vector_v)
    prim.CreatePointWeightsAttr(weights)
    prim.CreatePointsAttr(points)
    return prim


def reference_filename(stage, reference_name, fullpath=True, extension=None):
    filepath = str(stage.GetRootLayer().resolvedPath)  # .realPath
    if not extension:
        _, extension = os.path.splitext(filepath)
    filename = "%s%s" % (reference_name, extension)
    if fullpath:
        return os.path.join(os.path.dirname(filepath), filename)
    else:
        return filename


def prim_instance(stage, path, reference_name, xform=False, extension=None):
    from pxr import UsdGeom

    reference_filepath = reference_filename(stage, reference_name, fullpath=False, extension=extension)
    if not xform:
        ref = stage.OverridePrim(path)
        ref.GetReferences().AddReference("./%s" % reference_filepath)
    else:
        ref = UsdGeom.Xform.Define(stage, path)
        ref.GetPrim().GetReferences().AddReference("./%s" % reference_filepath)

    ref_xform = UsdGeom.Xformable(ref)
    ref_xform.SetXformOpOrder([])
    return ref


def translate_and_orient_from_frame(frame):
    from pxr import Gf

    w, x, y, z = Rotation.from_frame(frame).quaternion.wxyz
    return Gf.Vec3f(*frame.point), Gf.Quatd(w, x, y, z)


if __name__ == "__main__":
    from compas.geometry import NurbsSurface

    s = NurbsSurface()
