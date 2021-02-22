import math
from pxr import Gf
from compas.geometry import transpose_matrix, Rotation

def gfmatrix4d_from_transformation(transformation):
    return Gf.Matrix4d(*[v for col in transpose_matrix(transformation.matrix) for v in col])

def translate_and_rotateZYX_from_frame(frame):
    rotzyx = [math.degrees(a) for a in Rotation.from_frame(frame).euler_angles(False, 'xyz')]
    return Gf.Vec3f(*frame.point), Gf.Vec3f(*rotzyx)