import json
import asyncio
import websockets

from compas_xr.semiramis.messages import PoseArray
from compas_fab.backends.ros.messages import PoseStamped

subscriptions = [{'op': 'subscribe', 'topic': '/camera_pose'},
                 {'op': 'subscribe', 'topic': '/tree_poses'}]

address = "ws://localhost:9090"


async def subscribe(camera_queue, trees_queue):
    async with websockets.connect(address) as websocket:
        for subscribe_msg in subscriptions:
            await websocket.send(json.dumps(subscribe_msg))
            print(subscribe_msg)
        async for message in websocket:
            data = json.loads(message)
            if data['topic'] == '/camera_pose':
                pose_stamped = PoseStamped.from_msg(data['msg'])
                await camera_queue.put(pose_stamped.pose.frame)
            elif data['topic'] == '/tree_poses':
                poses = PoseArray.from_msg(data['msg']).poses
                frames = [pose.frame for pose in poses]
                await trees_queue.put(frames)


async def consumer(queue):
    """
    """
    while True:
        data = await queue.get()
        print(data)
        queue.task_done()


async def run():
    """
    """
    camera_queue = asyncio.Queue()
    trees_queue = asyncio.Queue()
    # schedule consumers
    consumer1 = asyncio.ensure_future(consumer(camera_queue))
    consumer2 = asyncio.ensure_future(consumer(trees_queue))
    await subscribe(camera_queue, trees_queue)
    await camera_queue.join()
    await trees_queue.join()
    # cancel consumers
    consumer1.cancel()
    consumer2.cancel()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
    # asyncio.ensure_future(run())
