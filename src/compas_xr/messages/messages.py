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


class MultiArrayDimension(ROSmsg):
    """http://docs.ros.org/en/api/std_msgs/html/msg/MultiArrayDimension.html
    """

    def __init__(self, label=None, size=0, stride=0):
        self.label = label or ""  # label of given dimension
        self.size = size  # size of given dimension (in type units)
        self.stride = stride  # stride of given dimension

    @classmethod
    def from_msg(cls, msg):
        return cls(msg['label'], msg['size'], msg['stride'])


class MultiArrayLayout(ROSmsg):
    """http://docs.ros.org/en/api/std_msgs/html/msg/MultiArrayLayout.html
    """

    def __init__(self, dim=None, data_offset=None):
        self.dim = dim or []
        self.data_offset = data_offset or 0

    @classmethod
    def from_msg(cls, msg):
        dim = msg['dim']
        return cls(dim, msg['data_offset'])


class Int8MultiArray(ROSmsg):
    """http://docs.ros.org/en/api/std_msgs/html/msg/Int8MultiArray.html
    """

    def __init__(self, layout=None, data=None):
        self.layout = layout or MultiArrayLayout()
        self.data = data or []

    @classmethod
    def from_msg(cls, msg):
        layout = MultiArrayLayout.from_msg(msg['layout'])
        return cls(layout, msg['data'])


class Float32MultiArray(ROSmsg):
    """http://docs.ros.org/en/api/std_msgs/html/msg/Float32MultiArray.html
    """

    def __init__(self, layout=None, data=None):
        self.layout = layout or MultiArrayLayout()
        self.data = data or []

    @classmethod
    def from_msg(cls, msg):
        layout = MultiArrayLayout.from_msg(msg['layout'])
        return cls(layout, msg['data'])


if __name__ == "__main__":
    from roslibpy import Topic
    from roslibpy import Ros
    import time

    client = Ros(host='localhost', port=9090)
    client.run()

    topic = Topic(client, '/testint8array', 'std_msgs/Int8MultiArray')
    topic.advertise()

    while True:

        hello_float = Int8MultiArray()
        hello_float.data = [1, 2, 3, 4]
        topic.publish(hello_float.msg)
        time.sleep(1)

    client.terminate()
