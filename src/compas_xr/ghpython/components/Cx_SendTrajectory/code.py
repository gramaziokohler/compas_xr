"""
Component to handle execution of trajectory.

Gets trajectories to be executed by a robot.

COMPAS XR v0.9.1
"""

from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve.ghpython import BackgroundWorker
from compas_eve.mqtt import MqttTransport
from ghpythonlib.componentbase import executingcomponent as component

from compas_xr.mqtt import SendTrajectory


def start_server(worker, options):
    topic_name_request = "compas_xr/send_trajectory/" + options.project_name

    worker.count = 0

    def execute_trajectory_requested(request_message):
        worker.count += 1
        worker.display_message("Request #{} started".format(worker.count))
        worker.update_result(request_message, 10)

    tx = MqttTransport(options.host)
    topic = Topic(topic_name_request, SendTrajectory)
    worker.subscriber = Subscriber(topic, callback=execute_trajectory_requested, transport=tx)
    worker.subscriber.subscribe()
    worker.display_message("Subscribed")


def stop_server(worker):
    if hasattr(worker, "subscriber"):
        worker.subscriber.unsubscribe()
    worker.display_message("Stopped")


class ExecuteTrajectoryServiceComponent(component):
    def RunScript(self, options, reset, on):
        if not on:
            BackgroundWorker.stop_instance_by_component(ghenv)  # noqa: F821
            return None

        self.worker = BackgroundWorker.instance_by_component(
            ghenv,  # noqa: F821
            start_server,
            dispose_function=stop_server,
            force_new=reset,
            auto_set_done=False,
            args=(options,),
        )

        if not self.worker.is_working() and not self.worker.is_done() and reset:
            self.worker.start_work()

        if hasattr(self.worker, "result"):
            element_id = self.worker.result.element_id
            robot_name = self.worker.result.robot_name
            return element_id, robot_name
        else:
            return None, None
