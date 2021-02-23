import asyncio

import omni.client
import omni.usd
from pxr import Usd
from pxr import UsdGeom

from compas.utilities import flatten


def open_stage(url):
    return Usd.Stage.Open(url)


def remove_mesh(stage_url, prim_path):
    stage = open_stage(stage_url)
    stage.RemovePrim(prim_path)
    stage.Save()
    omni.client.usd_live_process()


def add_mesh(stage_url, mesh, prim_path):
    omni.client.usd_live_wait_for_pending_updates()
    stage = open_stage(stage_url)

    meshPrim = UsdGeom.Mesh.Define(stage, prim_path)

    vertices, faces = mesh.to_vertices_and_faces()

    meshPrim.CreatePointsAttr(vertices)
    meshPrim.CreateFaceVertexCountsAttr([len(f) for f in faces])
    meshPrim.CreateFaceVertexIndicesAttr(list(flatten(faces)))

    stage.Save()
    omni.client.usd_live_process()

def add_meshes(stage_url, list_of_meshes_and_prim_paths):
    omni.client.usd_live_wait_for_pending_updates()
    stage = open_stage(stage_url)
    


    shell_meshes = list_of_meshes_and_prim_paths[0]
    shell_grass_meshes = list_of_meshes_and_prim_paths[1]
    column_meshes = list_of_meshes_and_prim_paths[2]
    site_meshes = list_of_meshes_and_prim_paths[3]

    for i, mesh in enumerate(shell_meshes):

        meshPrim = UsdGeom.Mesh.Define(stage, shell_meshes[i][1])
        vertices, faces = shell_meshes[i][0].to_vertices_and_faces()

        meshPrim.CreatePointsAttr(vertices)
        meshPrim.CreateFaceVertexCountsAttr([len(f) for f in faces])
        meshPrim.CreateFaceVertexIndicesAttr(list(flatten(faces)))
    
    for i, mesh in enumerate(shell_grass_meshes):

        meshPrim = UsdGeom.Mesh.Define(stage, shell_grass_meshes[i][1])
        vertices, faces = shell_grass_meshes[i][0].to_vertices_and_faces()

        meshPrim.CreatePointsAttr(vertices)
        meshPrim.CreateFaceVertexCountsAttr([len(f) for f in faces])
        meshPrim.CreateFaceVertexIndicesAttr(list(flatten(faces)))
    
    for i, mesh in enumerate(column_meshes):

        meshPrim = UsdGeom.Mesh.Define(stage, column_meshes[i][1])
        vertices, faces = column_meshes[i][0].to_vertices_and_faces()

        meshPrim.CreatePointsAttr(vertices)
        meshPrim.CreateFaceVertexCountsAttr([len(f) for f in faces])
        meshPrim.CreateFaceVertexIndicesAttr(list(flatten(faces)))
    
    for i, mesh in enumerate(site_meshes):

        meshPrim = UsdGeom.Mesh.Define(stage, site_meshes[i][1])
        vertices, faces = site_meshes[i][0].to_vertices_and_faces()

        meshPrim.CreatePointsAttr(vertices)
        meshPrim.CreateFaceVertexCountsAttr([len(f) for f in faces])
        meshPrim.CreateFaceVertexIndicesAttr(list(flatten(faces)))

    stage.Save()
    omni.client.usd_live_process()


def add_cylinder(stage_url, prim_path):
    #omni.client.usd_live_wait_for_pending_updates()
    print("hello")


