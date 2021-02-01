import xr_paths  # noqa F401

import omni.usd
import asyncio

from compas_xr.pxr import translate_and_rotateZYX_from_frame
from compas_xr.semiramis.communication import subscribe

url = "omniverse://localhost/Users/rr/semiramis/semiramis.project.usd"

async def open_stage(url):
    """Opens the stage.
    """
    omni.client.usd_live_set_default_enabled(True)
    await omni.usd.get_context().open_stage_async(url)
    context = omni.usd.get_context()
    context.set_stage_live(omni.usd.StageLiveModeType.ALWAYS_ON)
    return context.get_stage()


async def update_camera_pose(stage, queue):
    """Updates the camera pose.
    """
    camera = stage.GetPrimAtPath('/UserView')
    # omni.client.usd_live_wait_for_pending_updates() # needed?
    while True:
        #omni.client.usd_live_wait_for_pending_updates()
        frame = await queue.get()
        # M = gfmatrix4d_from_transformation(Transformation.from_frame(frame))
        # camera.GetAttribute('xformOp:transform').Set(M)
        translate, rotateZYX = translate_and_rotateZYX_from_frame(frame)
        camera.GetAttribute('xformOp:translate').Set(translate)
        camera.GetAttribute('xformOp:rotateZYX').Set(rotateZYX)
        stage.Save()
        omni.client.usd_live_process()
        queue.task_done()
        


async def update_trees_poses(stage, queue):
    """Updates the camera view.
    """
    # omni.client.usd_live_wait_for_pending_updates() # needed?
    while True:
        frames = await queue.get()
        persons = [stage.GetPrimAtPath('/Person%i' % i) for i in range(3)]
        for person, frame in zip(persons, frames):
            translate, rotateZYX = translate_and_rotateZYX_from_frame(frame)
            person.GetAttribute('xformOp:translate').Set(translate)
        stage.Save()
        omni.client.usd_live_process()
        queue.task_done()


async def run():
    """
    """
    # data from openvr
    camera_queue = asyncio.Queue()
    # data from gh
    trees_queue = asyncio.Queue()
    # omniverse stage
    stage = await open_stage(url)
    print("Stage opened")
    # schedule consumers
    consumer1 = asyncio.ensure_future(update_camera_pose(stage, camera_queue))
    consumer2 = asyncio.ensure_future(update_trees_poses(stage, trees_queue))
    # run the producer and wait for completion
    await subscribe(camera_queue, trees_queue)
    # wait until consumers have processed all items
    await camera_queue.join()
    await trees_queue.join()
    # cancel consumers
    consumer1.cancel()
    consumer2.cancel()

if __name__ == "__main__":
    asyncio.ensure_future(run())

"""
await context.save_as_stage_async(url)

// The stage is a sophisticated object that needs to be destroyed properly.  
// Since gStage is a smart pointer we can just reset it
gStage.Reset();

//omniClientTick(1000);
omni.client.shutdown()
"""

# kit.exe --enable omni.usd --enable omni.client --exec C:\Users\rustr\workspace\compas_xr\src\compas_xr\semiramis\main.py
