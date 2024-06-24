"""
Component to define COMPAS XR options.

COMPAS XR v0.9.1
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_xr.ghpython import MqttMessageOptionsXR


class XrOptionsComponent(component):
    def RunScript(self, host, project_name, robot_name):
        return MqttMessageOptionsXR(host, project_name, robot_name)
