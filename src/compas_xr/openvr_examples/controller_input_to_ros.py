"""
k_EButton_A = 7
k_EButton_ApplicationMenu = 1
k_EButton_Axis0 = 32
k_EButton_Axis1 = 33
k_EButton_Axis2 = 34
k_EButton_Axis3 = 35
k_EButton_Axis4 = 36
k_EButton_DPad_Down = 6
k_EButton_DPad_Left = 3
k_EButton_DPad_Right = 5
k_EButton_DPad_Up = 4
k_EButton_Dashboard_Back = 2
k_EButton_Grip = 2
k_EButton_IndexController_A = 2
k_EButton_IndexController_B = 1
k_EButton_IndexController_JoyStick = 35
k_EButton_Max = 64
k_EButton_ProximitySensor = 31
k_EButton_SteamVR_Touchpad = 32
k_EButton_SteamVR_Trigger = 33
k_EButton_System = 0


openvr.VREvent_ButtonTouch
openvr.VREvent_ButtonUntouch
openvr.VREvent_ButtonPress
openvr.VREvent_ButtonUnpress

# https://gist.github.com/awesomebytes/75daab3adb62b331f21ecf3a03b3ab46

# pose = poses[i]
        # pose_info = dict(
        #    model_name=model_name,
        #    device_is_connected=pose.bDeviceIsConnected,
        #    device_is_controller=is_controller,
        #    valid=pose.bPoseIsValid,
        #    tracking_result=pose.eTrackingResult,
        #    d2a=pose.mDeviceToAbsoluteTracking,
        #    velocity=pose.vVelocity,                   # m/s
        #    angular_velocity=pose.vAngularVelocity     # radians/s?
        # )
"""

import openvr

from roslibpy import Topic
from roslibpy import Ros

from compas_fab.backends.ros.messages import Pose
from compas_fab.backends.ros.messages import PoseStamped
from compas.geometry import Transformation
from compas.geometry import Frame

from compas_xr.messages import Int8MultiArray
from compas_xr.messages import Float32MultiArray

# ros
client = Ros(host='localhost', port=9090)
client.run()

model_names = ['generic_hmd', 'controller_left', 'controller_right', 'OptiTrackRigidBody', 'lh_basestation_valve_gen2']
position_talkers = dict(zip(model_names, [Topic(client, '/position_%s' % name, 'geometry_msgs/PoseStamped') for name in model_names]))
hands = ["left", "right"]
hands_idx = dict(zip(hands, [None for _ in range(len(hands))]))

buttonpress_talker = dict(zip(hands, [Topic(client, '/buttonpress_%s' % hand, 'std_msgs/Int8MultiArray') for hand in hands]))
trackpad_talker = dict(zip(hands, [Topic(client, '/trackpad_%s' % hand, 'std_msgs/Float32MultiArray') for hand in hands]))

button_idx = [openvr.k_EButton_SteamVR_Trigger, openvr.k_EButton_SteamVR_Touchpad, openvr.k_EButton_Grip, openvr.k_EButton_A, openvr.k_EButton_IndexController_B]
button_values = [0 for _ in range(len(button_idx))]

for d in [position_talkers, buttonpress_talker, trackpad_talker]:
    for k, topic in d.items():
        topic.advertise()

openvr.init(openvr.VRApplication_Scene)


def get_model_name(vrsys, dix, device_class):
    if device_class == openvr.TrackedDeviceClass_Controller:
        if vrsys.getControllerRoleForTrackedDeviceIndex(dix) == openvr.TrackedControllerRole_RightHand:
            model_name = 'controller_right'
        else:
            model_name = 'controller_left'
    else:
        model_name = vrsys.getStringTrackedDeviceProperty(dix, openvr.Prop_RenderModelName_String)
    return model_name


while client.is_connected:

    poses, _ = openvr.VRCompositor().waitGetPoses([], None)
    vrsys = openvr.VRSystem()

    for i, pose in enumerate(poses):

        device_class = vrsys.getTrackedDeviceClass(i)
        if device_class == openvr.TrackedDeviceClass_Invalid:
            continue
        is_controller = device_class == openvr.TrackedDeviceClass_Controller
        is_beacon = device_class == openvr.TrackedDeviceClass_TrackingReference

        # only once needed
        if device_class == openvr.TrackedDeviceClass_Controller:
            if vrsys.getControllerRoleForTrackedDeviceIndex(i) == openvr.TrackedControllerRole_RightHand:
                hands_idx["right"] = i
            else:
                hands_idx["left"] = i

        model_name = get_model_name(vrsys, i, device_class)

        T = Transformation(list(poses[i].mDeviceToAbsoluteTracking) + [[0, 0, 0, 1]])
        pose_msg = Pose.from_frame(Frame.from_transformation(T))
        pose_stamped_msg = PoseStamped(pose=pose_msg)
        position_talkers[model_name].publish(pose_stamped_msg.msg)

    hands_idx_inv = {v: k for k, v in hands_idx.items()}
    vrsys = openvr.VRSystem()

    # controllers
    for hand, dix in hands_idx.items():
        result, pControllerState = vrsys.getControllerState(dix)

        trackpad_x = pControllerState.rAxis[0].x
        trackpad_y = pControllerState.rAxis[0].y
        trackpad_touched = bool(pControllerState.ulButtonTouched >> 32 & 1)
        if trackpad_touched:
            print(trackpad_x, trackpad_y)
            msg = Float32MultiArray(data=[trackpad_x, trackpad_y])
            trackpad_talker[hand].publish(msg.msg)

    # button presses

    new_event = openvr.VREvent_t()

    while vrsys.pollNextEvent(new_event):

        dix = new_event.trackedDeviceIndex
        device_class = vrsys.getTrackedDeviceClass(dix)
        if device_class == openvr.TrackedDeviceClass_Controller:
            hand = hands_idx_inv[dix]
            bix = new_event.data.controller.button
            if bix in button_idx:
                i = button_idx.index(bix)
                if new_event.eventType == openvr.VREvent_ButtonPress:
                    button_values[i] = 1
                if new_event.eventType == openvr.VREvent_ButtonUnpress:
                    button_values[i] = 0
                print(button_values)
                # button_state_talker.publish()
                msg = Int8MultiArray(data=button_values)
                buttonpress_talker[hand].publish(msg.msg)


for d in [position_talkers, buttonpress_talker, trackpad_talker]:
    for k, topic in d.items():
        topic.unadvertise()

client.terminate()

openvr.shutdown()
