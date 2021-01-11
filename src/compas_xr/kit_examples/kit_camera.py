import sys
sys.path.append('C:\\Users\\rustr\\.conda\\envs\\xr\\lib\\site-packages')
import roslibpy
from roslibpy import Topic
from roslibpy import Ros
import omni.usd
import asyncio
import time

def topic_callback(msg):
    print(msg)

async def task():
    client = Ros(host='localhost', port=9090)
    client.run()
    
    topic = Topic(client, '/camera_position', 'geometry_msgs/PoseStamped')
    topic.subscribe(topic_callback)
    
    omni.client.usd_live_set_default_enabled(True)
    url = "omniverse://localhost/Users/rr/semiramis/semiramis.project.usd"
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
    await omni.usd.get_context().save_as_stage_async(url)
    time.sleep(1)
    client.terminate()
    
asyncio.ensure_future(task())









