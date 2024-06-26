"""
Planning service response.

COMPAS XR v1.0.0
"""

from compas_eve import Publisher
from compas_eve import Topic
from compas_eve.mqtt import MqttTransport
from ghpythonlib.componentbase import executingcomponent as component

from compas_xr.mqtt import GetTrajectoryResult


class PlanningServiceResponseComponent(component):
    def RunScript(self, options, result, publish):
        if not result:
            self.Message = "Null Result, unable to publish"
            return

        if publish:
            topic_name_result = "compas_xr/get_trajectory_result/" + options.project_name
            topic = Topic(topic_name_result, GetTrajectoryResult)
            tx = MqttTransport(options.host)
            publisher = Publisher(topic, transport=tx)
            message = GetTrajectoryResult(
                element_id=result.requested_element_id,
                robot_name=options.robot_name,
                robot_base_frame=result.robot_base_frame,
                trajectory=result.trajectory,
                pick_and_place=result.pick_and_place,
                pick_index=result.pick_index,
                end_effector_link_name=result.end_effector_link_name,
            )
            publisher.publish(message)
            self.Message = "Send trajectory for #{}".format(result.requested_element_id)
