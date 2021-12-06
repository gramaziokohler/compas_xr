import omni.client
import omni.usd
from pxr import Usd
from pxr import UsdGeom

from compas.utilities import flatten

# C:\Users\rustr\AppData\Local\ov\pkg\connectsample-103.1.0\source\pyHelloWorld


def open_stage(url):
    return Usd.Stage.Open(url)


async def open_stage_live(url):
    """Opens the stage.
    """
    omni.client.usd_live_set_default_enabled(True)
    context = omni.usd.get_context()
    stage = Usd.Stage.Open(url)
    context.set_stage_live(omni.usd.StageLiveModeType.ALWAYS_ON)
    return stage
    # await context.open_stage_async(url)
    # return context.get_stage()


async def save_stage(stage):
    stage.GetRootLayer().Save()
    omni.client.usd_live_process()


def start_omniverse():
    """Startup Omniverse."""
    """
    # Register a function to be called whenever the library wants to print something to a log
    omni.client.set_log_callback(logCallback)

    # The default log level is "Info", set it to "Debug" to see all messages
    omni.client.set_log_level(eOmniClientLogLevel_Debug)

    # Initialize the library and pass it the version constant defined in OmniClient.h
    # This allows the library to verify it was built with a compatible version. It will
    # return false if there is a version mismatch.
    if not omni.client.initialize(kOmniClientVersion):
        return EXIT_FAILURE
    omni.client.register_connection_status_callback(OmniClientConnectionStatusCallbackImpl)
    """
    omni.client.usd_live_set_default_enabled(True)  # Enable live updates
    return True


def shutdown_omniverse():
    """Shut down Omniverse connection."""
    omni.client.usd_live_wait_for_pending_updates()
    omni.client.shutdown()


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
