import sys

paths = ['C:\\Users\\rustr\\.conda\\envs\\xr\\DLLs', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib', 'C:\\Users\\rustr\\.conda\\envs\\xr', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\matplotlib-3.0.3-py3.6-win-amd64.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\imageio-2.9.0-py3.6.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\watchdog-0.10.4-py3.6.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\sympy-1.7rc1-py3.6.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\scipy-1.5.4-py3.6-win-amd64.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\jsonschema-3.2.0-py3.6.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\schema-0.7.3-py3.6.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\pycollada-0.7.1-py3.6.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\planarity-0.4.1-py3.6-win-amd64.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\numpy-1.19.3-py3.6-win-amd64.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\numba-0.52.0rc3-py3.6-win-amd64.egg', 'C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages\\networkx-2.5-py3.6.egg', 'c:\\users\\rustr\\workspace\\compas_xr\\src', 'c:\\users\\rustr\\workspace\\libraries\\pyopenvr\\src']
for path in paths:
    sys.path.append(path)

from compas_fab.backends import RosClient
from compas_fab.backends.ros.messages import PoseStamped
from roslibpy import Topic
from roslibpy import Ros
import omni.usd
import asyncio
import time

url = "omniverse://localhost/Users/rr/semiramis/semiramis.project.usd"


def topic_callback(msg):
    print(msg)
    frame = PoseStamped.from_msg(msg).pose.frame
    print(frame)


async def task():
    omni.client.usd_live_set_default_enabled(True)
    await omni.usd.get_context().open_stage_async(url)
    context = omni.usd.get_context()
    stage = context.get_stage()
    camera = stage.GetPrimAtPath('/World/Default/Cameras/camera_default')
    #for x in dir(camera):
    #   print(x)
    #camera = geom_camera.GetCamera()
    print(camera.GetPropertyNames())
    attr = camera.GetAttribute('xformOp:transform')
    print(attr)
    print(attr.Get())
    # attr.Set(pose) # update from topic
    await omni.usd.get_context().save_as_stage_async(url)

with RosClient() as client:
    topic = Topic(client, '/camera_position', 'geometry_msgs/PoseStamped')
    topic.subscribe(topic_callback)
    asyncio.ensure_future(task())
    time.sleep(1)

