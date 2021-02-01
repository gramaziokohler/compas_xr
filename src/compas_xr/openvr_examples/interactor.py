import openvr

from compas.geometry import Transformation
from compas.geometry import Frame

Fy_up = Frame((0, 0, 0), (1, 0, 0), (0, 0, -1))
Fz_up = Frame((0, 0, 0), (1, 0, 0), (0, 1, 0))
T2z_up = Transformation.from_frame_to_frame(Fy_up, Fz_up)


class ControllerState(object):
    """
    """

    def __init__(self, name):
        self.name = name
        self.is_pressed = False
        self.is_dragging = False
        self.device_index = None
        self.current_frame = None
        self.previous_frame = None


class Interactor(object):
    """Composite interactor consisting of both controllers plus maybe other inputs.
    """

    def __init__(self):
        self.left_controller = ControllerState("left controller")
        self.right_controller = ControllerState("right controller")
        self.velocity_damping = 1.5  # meters per second per second
        self.speed = 0.0  # meters per second inertial velocity
        self.min_velocity = 0.01  # meters per second

    def update_controller_states(self):
        self._compute_controller_frames()
        new_event = openvr.VREvent_t()
        while openvr.VRSystem().pollNextEvent(new_event):
            self._check_controller_status(new_event)

    def _check_controller_status(self, event):
        dix = event.trackedDeviceIndex
        device_class = openvr.VRSystem().getTrackedDeviceClass(dix)
        if device_class != openvr.TrackedDeviceClass_Controller:
            return
        bix = event.data.controller.button
        # Pay attention to trigger presses only
        if bix != openvr.k_EButton_SteamVR_Trigger:
            return
        role = openvr.VRSystem().getControllerRoleForTrackedDeviceIndex(dix)
        if role == openvr.TrackedControllerRole_RightHand:
            controller = self.right_controller
        else:
            controller = self.left_controller
        controller.device_index = dix
        t = event.eventType
        # "Touch" event happens earlier than "Press" event,
        # so allow a light touch for grabbing here
        if t == openvr.VREvent_ButtonTouch:
            controller.is_dragging = True
        elif t == openvr.VREvent_ButtonUntouch:
            controller.is_dragging = False
        elif t == openvr.VREvent_ButtonPress:
            controller.is_pressed = True
        elif t == openvr.VREvent_ButtonUnpress:
            controller.is_pressed = False

    def _compute_controller_frames(self):
        poses, _ = openvr.VRCompositor().waitGetPoses([], None)
        vrsys = openvr.VRSystem()
        for dix, pose in enumerate(poses):
            device_class = vrsys.getTrackedDeviceClass(dix)
            if device_class == openvr.TrackedDeviceClass_Invalid or device_class != openvr.TrackedDeviceClass_Controller:
                continue
            role = openvr.VRSystem().getControllerRoleForTrackedDeviceIndex(dix)
            controller = self.right_controller if role == openvr.TrackedControllerRole_RightHand else self.left_controller
            T = Transformation(list(pose.mDeviceToAbsoluteTracking) + [[0, 0, 0, 1]])
            frame = Frame.from_transformation(T).transformed(T2z_up)
            controller.previous_frame = controller.current_frame
            controller.current_frame = frame
