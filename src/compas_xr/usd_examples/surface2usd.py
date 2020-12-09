import os
import numpy as np
from pxr import Usd
from pxr import UsdGeom
from compas.utilities import flatten
from compas_xr import DATA

filepath = os.path.join(DATA, "surface.usda")

stage = Usd.Stage.CreateNew('surface.usda')
xformPrim = UsdGeom.Xform.Define(stage, '/hello')

degree_u, degree_v = 3, 3
knot_vector_u = [0.0, 0.0, 0.0, 1.614, 1.614, 1.614]
knot_vector_v = [0.0, 0.0, 0.0, 1.639, 2.459, 3.279, 4.918, 4.918, 4.918]
knot_vector_u = [knot_vector_u[0]] + knot_vector_u + [knot_vector_u[-1]]
knot_vector_v = [knot_vector_v[0]] + knot_vector_v + [knot_vector_v[-1]]
count_u = len(knot_vector_u) - 1 - degree_u
count_v = len(knot_vector_v) - 1 - degree_v

points = [[-1.064, 0.0, 0.496], [-0.844, 0.0, 1.161], [-0.362, 0.0, 1.32], [0.414, 0.0, 1.104], [1.221, 0.0, 1.019], [1.597, 0.0, 1.276], [1.51, 0.0, 1.744], [-1.13, 0.343, 0.762], [-0.732, 0.343, 1.56], [-0.283, 0.343, 1.474], [0.326, 0.343, 1.086], [0.964, 0.343, 0.839], [1.364, 0.343, 0.978], [1.345, 0.343, 1.633], [-1.196, 0.685, 1.027], [-0.62, 0.685, 1.959], [-0.205, 0.685, 1.629], [0.238, 0.685, 1.069], [0.706, 0.685, 0.659], [1.131, 0.685, 0.68], [1.18, 0.685, 1.521], [-1.262, 1.028, 1.292], [-0.507, 1.028, 2.359], [-0.127, 1.028, 1.783], [0.149, 1.028, 1.051], [0.449, 1.028, 0.479], [0.897, 1.028, 0.381], [1.014, 1.028, 1.409]]
weights = [1.] * len(points)

nurbsPrim = UsdGeom.NurbsPatch.Define(stage, "/hello/surface")
nurbsPrim.CreateUVertexCountAttr(count_u)
nurbsPrim.CreateVVertexCountAttr(count_v)
nurbsPrim.CreateUOrderAttr(4)
nurbsPrim.CreateVOrderAttr(4)
nurbsPrim.CreateUKnotsAttr(knot_vector_u)
nurbsPrim.CreateVKnotsAttr(knot_vector_v)
# nurbsPrim.CreateURangeAttr(knot_vector_u[-1])
# nurbsPrim.CreateVRangeAttr(Vt.Vec2dArray([knot_vector_v[0], knot_vector_v[-1]]))
nurbsPrim.CreatePointWeightsAttr(weights)


points = np.reshape(points, (count_u, count_v, 3))
points = points.transpose((1, 0, 2))
points = list(flatten(points))


nurbsPrim.CreatePointsAttr(points)
print(nurbsPrim.GetURangeAttr().Get())
print(nurbsPrim.GetPointWeightsAttr().Get())
print(nurbsPrim.GetUFormAttr().Get())
# CreateURangeAttr
# CreateUVertexCountAttr

stage.GetRootLayer().Save()
