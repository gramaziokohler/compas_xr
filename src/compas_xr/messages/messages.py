from compas_fab.backends.ros.messages import Header
from compas_fab.backends.ros.messages import ROSmsg
from compas_fab.backends.ros.messages import Pose

class PoseArray(ROSmsg):
    """http://docs.ros.org/en/api/geometry_msgs/html/msg/PoseArray.html

    TODO: move to compas_fab.backends.ros.messages
    """

    def __init__(self, header=None, poses=None):
        self.header = header or Header()
        self.poses = poses or []

    @classmethod
    def from_msg(cls, msg):
        header = Header.from_msg(msg['header'])
        poses = [Pose.from_msg(p) for p in msg['poses']]
        return cls(header, poses)
