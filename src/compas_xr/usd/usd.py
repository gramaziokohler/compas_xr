
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import math
from compas.utilities import flatten

from compas.geometry import transpose_matrix
from compas.geometry import Frame
from compas.geometry import Rotation
from compas.geometry import Transformation


def apply_frame_transformation_on_prim(prim, frame):
    """
    """
    from pxr import UsdGeom
    xform = UsdGeom.Xformable(prim)
    transform = xform.AddTransformOp()
    matrix = gfmatrix4d_from_transformation(Transformation.from_frame(frame))
    transform.Set(matrix)


def apply_rotate_and_translate_on_prim(prim, frame):
    from pxr import UsdGeom
    _, _, _, _, rotOrder = UsdGeom.XformCommonAPI(prim).GetXformVectors(0)

    switcher = {UsdGeom.XformCommonAPI.RotationOrderXYZ: "xyz",
                UsdGeom.XformCommonAPI.RotationOrderXZY: "xzy",
                UsdGeom.XformCommonAPI.RotationOrderYXZ: "yxz",
                UsdGeom.XformCommonAPI.RotationOrderYZX: "yzx",
                UsdGeom.XformCommonAPI.RotationOrderZXY: "zxy",
                UsdGeom.XformCommonAPI.RotationOrderZYX: "zyx"}

    axes = switcher.get(rotOrder, None)
    euler_angles = [math.degrees(a) for a in frame.euler_angles(False, axes)]
    UsdGeom.XformCommonAPI(prim).SetRotate(euler_angles)
    UsdGeom.XformCommonAPI(prim).SetTranslate(tuple(frame.point))


def prim_from_box(stage, path, box):
    """Returns a `UsdGeom.Cube`

    >>> box = Box(Frame.worldXY(), 1, 1, 1)
    >>> prim_from_box(stage, "/box", box)
    UsdGeom.Cube(Usd.Prim(</box>))
    """
    from pxr import UsdGeom
    prim = UsdGeom.Cube.Define(stage, path)
    prim.GetPrim().GetAttribute('size').Set(1.0)
    UsdGeom.XformCommonAPI(prim).SetScale((box.xsize, box.ysize, box.zsize))
    apply_rotate_and_translate_on_prim(prim, box.frame)
    return prim


def prim_from_sphere(stage, path, sphere):
    """Returns a ``pxr.UsdGeom.Sphere``

    >>> sphere = Sphere((0, 0, 0), 5)
    >>> prim_from_sphere(stage, "/sphere", sphere)
    UsdGeom.Sphere(Usd.Prim(</sphere>))
    """
    from pxr import UsdGeom
    prim = UsdGeom.Sphere.Define(stage, path)
    prim.GetPrim().GetAttribute('radius').Set(sphere.radius)
    UsdGeom.XformCommonAPI(prim).SetTranslate(tuple(sphere.point))
    return prim


def prim_from_mesh(stage, path, mesh):
    """Returns a ``pxr.UsdGeom.Mesh``

    >>> box = Box(Frame.worldXY(), 1, 1, 1)
    >>> mesh = Mesh.from_shape(box)
    >>> prim_from_mesh(stage, "/mesh", mesh)
    UsdGeom.Mesh(Usd.Prim(</mesh>))
    """
    from pxr import UsdGeom
    prim = UsdGeom.Mesh.Define(stage, path)
    vertices, faces = mesh.to_vertices_and_faces()
    prim.CreatePointsAttr(vertices)
    prim.CreateFaceVertexCountsAttr([len(f) for f in faces])
    prim.CreateFaceVertexIndicesAttr(list(flatten(faces)))
    return prim


def prim_from_surface(stage, path, surface):
    """Returns a ``pxr.UsdGeom.NurbsPatch``

    >>> control_points = [[[0, 0, 0], [0, 4, 0], [0, 8, -3]], [[2, 0, 6], [2, 4, 0], [2, 8, 0]], [[4, 0, 0], [4, 4, 0], [4, 8, 3]], [[6, 0, 0], [6, 4, -3], [6, 8, 0]]]
    >>> degree = (3, 2)
    >>> surface = Surface(control_points, degree)
    >>> prim_from_surface(stage, "/surface", surface)
    UsdGeom.NurbsPatch(Usd.Prim(</surface>))
    """
    from pxr import UsdGeom
    from compas_nurbs.utilities import unflatten
    from compas.utilities import flatten
    from compas.geometry import transpose_matrix

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


def prim_default(stage, path, frame=None):
    """
    """
    from pxr import UsdGeom
    prim = UsdGeom.Xform.Define(stage, path)
    if frame:
        apply_frame_transformation_on_prim(prim, frame)
    return prim


def reference_filename(stage, reference_name, fullpath=True):
    filepath = str(stage.GetRootLayer().resolvedPath)  # .realPath
    _, extension = os.path.splitext(filepath)
    filename = "%s%s" % (reference_name, extension)
    if fullpath:
        return os.path.join(os.path.dirname(filepath), filename)
    else:
        return filename


def prim_instance(stage, path, reference_name):
    from pxr import UsdGeom
    ref = stage.OverridePrim(path)
    reference_filepath = reference_filename(stage, reference_name, fullpath=False)
    ref.GetReferences().AddReference('./%s' % reference_filepath)
    ref_xform = UsdGeom.Xformable(ref)
    ref_xform.SetXformOpOrder([])
    return ref


def gfmatrix4d_from_transformation(transformation):
    from pxr import Gf
    return Gf.Matrix4d(*[v for col in transpose_matrix(transformation.matrix) for v in col])


def translate_and_orient_from_frame(frame):
    from pxr import Gf
    w, x, y, z = Rotation.from_frame(frame).quaternion.wxyz
    return Gf.Vec3f(*frame.point), Gf.Quatd(w, x, y, z)


def frame_from_translate_and_rotateZYX(translate, rotateZYX):
    rotateZYX_radians = [math.radians(a) for a in list(rotateZYX)]
    return Frame.from_euler_angles(rotateZYX_radians, static=False, axes='xyz', point=translate)


if __name__ == "__main__":
    import doctest
    from pxr import Usd
    from compas.geometry import Box  # noqa F401
    from compas.geometry import Sphere  # noqa F401
    from compas.geometry import Frame  # noqa F401
    from compas.datastructures import Mesh  # noqa F401
    from compas_nurbs import Surface  # noqa F401

    stage = Usd.Stage.CreateInMemory()
    doctest.testmod()
