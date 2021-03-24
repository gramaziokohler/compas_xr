import math

from pxr import Gf

from compas.geometry import Frame
from compas.geometry import Rotation
from compas.geometry import transpose_matrix


def gfmatrix4d_from_transformation(transformation):
    return Gf.Matrix4d(*[v for col in transpose_matrix(transformation.matrix) for v in col])


def translate_and_rotateZYX_from_frame(frame):
    rotzyx = [math.degrees(a) for a in Rotation.from_frame(frame).euler_angles(False, 'xyz')]
    return Gf.Vec3f(*frame.point), Gf.Vec3f(*rotzyx)


def frame_from_translate_and_rotateZYX(translate, rotateZYX):
    rotateZYX_radians = [math.radians(a) for a in list(rotateZYX)]
    return Frame.from_euler_angles(rotateZYX_radians, static=False, axes='xyz', point=translate)
