import asyncio

from pxr import Usd
from pxr import UsdGeom

from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.utilities import flatten


def sphere_to_usd_mesh(filepath):
    mesh = Mesh.from_shape(Sphere((0, 0, 0), 2.))
    mesh_to_usd_mesh(mesh, filepath)


def mesh_to_usd_mesh(mesh, filepath, mesh_prim='/main/mesh'):
    stage = Usd.Stage.CreateNew(filepath)
    meshPrim = UsdGeom.Mesh.Define(stage, mesh_prim)

    vertices, faces = mesh.to_vertices_and_faces()

    meshPrim.CreatePointsAttr(vertices)
    meshPrim.CreateFaceVertexCountsAttr([len(f) for f in faces])
    meshPrim.CreateFaceVertexIndicesAttr(list(flatten(faces)))

    stage.GetRootLayer().Save()
