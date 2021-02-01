import math
import openvr
from compas_xr.openvr_examples.interactor import Interactor
from compas_xr.semiramis.camera_position import camera_position
from compas_fab.backends.ros.messages import Pose, PoseStamped
from compas.geometry import Point
from compas_fab.utilities.numbers import map_range
from compas_fab.backends.ros import RosClient

from roslibpy import Topic


openvr.init(openvr.VRApplication_Scene)
interactor = Interactor()

dx_range = [0.10146443545818329, 1.6]
z_range = [-0.3,  0.9]


def clamp(v, vmin, vmax):
    return(max(min(v, vmax), vmin))


target = Point(0, 0, 1029)
radius = 4438
zvalue = 330
increment = 0.0
angle = 0

z_increment = 0
import time

with RosClient() as client:

    topic = Topic(client, "/camera_pose", "geometry_msgs/PoseStamped")
    topic.advertise()

    while client.is_connected:

        interactor.update_controller_states()
        if interactor.left_controller.is_pressed and interactor.right_controller.is_pressed:
            f1 = interactor.left_controller.current_frame
            f2 = interactor.right_controller.current_frame
            print("boths")
            # target
            # radius
            # zvalue
            # increment == speed
            distance = math.fabs(f1.point.x - f2.point.x)  # the higher the more speed
            increment = map_range(distance, dx_range[0], dx_range[1], -2, 10)
            increment = clamp(increment, 0, 10)

            print("increment", increment)
            zvalue = (f1.point.z + f2.point.z)/2.
            z_increment = map_range(zvalue, z_range[0], z_range[1], -10, 10)
            z_increment = clamp(z_increment, -10, 10)
            print("z_increment", z_increment)

        angle += increment
        #target.z += z_increment
        if angle > 360:
            angle -= 360
        #print(angle)
        frame = camera_position(target, math.radians(angle), radius, zvalue)
        print(frame)
        pose_msg = Pose.from_frame(frame)
        pose_stamped_msg = PoseStamped(pose=pose_msg)
        topic.publish(pose_stamped_msg.msg)
        time.sleep(0.05)

openvr.shutdown()
