import os
from pxr import Usd
from pxr import UsdGeom
from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.utilities import flatten

from compas_xr import DATA

filepath = os.path.join(DATA, "mesh.usda")

stage = Usd.Stage.CreateNew(filepath)
xformPrim = UsdGeom.Xform.Define(stage, '/hello')
meshPrim = UsdGeom.Mesh.Define(stage, "/hello/mesh")

mesh = Mesh.from_shape(Sphere((0, 0, 0), 2.))
vertices, faces = mesh.to_vertices_and_faces()

meshPrim.CreatePointsAttr(vertices)
meshPrim.CreateFaceVertexCountsAttr([len(f) for f in faces])
meshPrim.CreateFaceVertexIndicesAttr(list(flatten(faces)))

stage.GetRootLayer().Save()
