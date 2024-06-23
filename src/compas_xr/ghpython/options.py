class MqttMessageOptionsXR(object):

    def __init__(self, host, project_name, robot_name):
        self.host = host
        self.project_name = project_name
        self.robot_name = robot_name

    def ToString(self):
        return str(self)

    def __str__(self):
        return "Options, host={}, project_name={}, robot_name={}".format(self.host, self.project_name, self.robot_name)
