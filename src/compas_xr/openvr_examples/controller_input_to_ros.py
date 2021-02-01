import openvr

from roslibpy import Topic
from roslibpy import Ros
from roslibpy import Message

from compas_fab.backends.ros.messages import Pose, PoseStamped
from compas.geometry import Transformation, Frame

# ros
client = Ros(host='localhost', port=9090)
client.run()

model_names = ['generic_hmd', 'controller_left', 'controller_right']
position_talkers = dict(zip(model_names, [Topic(client, '/position_%s' % name, 'geometry_msgs/PoseStamped') for name in model_names]))
button_talkers = dict(zip(model_names, [Topic(client, '/button_%s' % name, 'std_msgs/String') for name in model_names]))

for k, topic in position_talkers.items():
    topic.advertise()
for k, topic in button_talkers.items():
    topic.advertise()

openvr.init(openvr.VRApplication_Scene)

def get_model_name(vrsys, dix, device_class):
    """
    """
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

        model_name = get_model_name(vrsys, i, device_class)

        """
        pose = poses[i]
        pose_info = dict(
            model_name=model_name,
            device_is_connected=pose.bDeviceIsConnected,
            device_is_controller=is_controller,
            valid=pose.bPoseIsValid,
            tracking_result=pose.eTrackingResult,
            d2a=pose.mDeviceToAbsoluteTracking,
            velocity=pose.vVelocity,                   # m/s
            angular_velocity=pose.vAngularVelocity     # radians/s?
        )
        """
        T = Transformation(list(poses[i].mDeviceToAbsoluteTracking) + [[0, 0, 0, 1]])
        pose_msg = Pose.from_frame(Frame.from_transformation(T))
        pose_stamped_msg = PoseStamped(pose=pose_msg)
        position_talkers[model_name].publish(pose_stamped_msg.msg)
    
    new_event = openvr.VREvent_t()
    vrsys = openvr.VRSystem()

    while vrsys.pollNextEvent(new_event):

        dix = new_event.trackedDeviceIndex
        device_class = vrsys.getTrackedDeviceClass(dix)
        # We only want to watch controller events
        if device_class != openvr.TrackedDeviceClass_Controller:
            continue
        model_name = get_model_name(vrsys, dix, device_class)
        bix = new_event.data.controller.button
        # Pay attention to trigger presses only
        if bix != openvr.k_EButton_SteamVR_Trigger:
            #print("bix", bix)
            continue
        device_index = dix
        t = new_event.eventType
        actions = {openvr.VREvent_ButtonTouch : "touch",
                   openvr.VREvent_ButtonUntouch : "untouch",
                   openvr.VREvent_ButtonPress : "press",
                   openvr.VREvent_ButtonUnpress : "unpress",}        
        button_talkers[model_name].publish(Message({'data': actions[t]}))

for name in model_names:
    position_talkers[name].unadvertise()
    button_talkers[name].unadvertise()

client.terminate()

openvr.shutdown()
