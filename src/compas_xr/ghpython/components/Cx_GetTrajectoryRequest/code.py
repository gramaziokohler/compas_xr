"""
Get Trajectory Request Component.

A custom Compas Eve MQTT Subscriber component for receiving planning requests from the application.

COMPAS XR v0.1.0
"""

from ghpythonlib.componentbase import executingcomponent as component
import functools
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import time
import threading

from compas.data import json_dump
from compas_eve import Message
from compas_eve import Topic
from compas_eve import Subscriber
from compas_eve.mqtt import MqttTransport
from compas_eve.ghpython import BackgroundWorker
from compas_xr.mqtt import GetTrajectoryRequest


def start_server(worker, options):
    topic_name_request = 'compas_xr/get_trajectory_request/' + options.project_name

    worker.count = 0
    
    def get_trajectory_requested(request_message):
        worker.count += 1
        worker.display_message("Request #{} started".format(worker.count))
        worker.update_result(request_message, 10)

    tx = MqttTransport(options.host)
    topic = Topic(topic_name_request, GetTrajectoryRequest)
    worker.subscriber = Subscriber(topic, callback=get_trajectory_requested, transport=tx)
    worker.subscriber.subscribe()
    worker.display_message("Subscribed")

def stop_server(worker):
    if hasattr(worker, "subscriber"):
        worker.subscriber.unsubscribe()
    worker.display_message("Stopped")


class BackgroundTaskComponent(component):
    def RunScript(self, options, reset, on):
        if not on:
            BackgroundWorker.stop_instance_by_component(ghenv)  # noqa: F821
            return None

        self.worker = BackgroundWorker.instance_by_component(ghenv, start_server, dispose_function=stop_server, force_new=reset, auto_set_done=False, args=(options,))  # noqa: F821

        if not self.worker.is_working() and not self.worker.is_done() and reset:
            self.worker.start_work()

        print("Worker ID: {}".format(id(self.worker)))
        print("Is worker running? {}".format(self.worker.is_working()))
        print("Worker completed? {}".format(self.worker.is_done()))
        if hasattr(self.worker, "thread"):
            print("Worker thread: {}".format(self.worker.thread))

        DEBUG = False
        if DEBUG:
            other_workers = []
            for key in sc.sticky.keys():
                if key.startswith("background_worker_"):
                    worker = sc.sticky[key]
                    if worker != self.worker:
                        other_workers.append(worker)

            if len(other_workers):
                print
                print("Found {} more workers:".format(len(other_workers)))
                for worker in other_workers:
                    print("* Worker ID: {}".format(id(worker)))
                    print(" - Is worker running? {}".format(worker.is_working()))
                    print(" - Worker completed? {}".format(worker.is_done()))
                    print(" - Worker thread: {}".format(worker.thread))

            non_main_threads = [thread for thread in threading.enumerate() if thread.name != "MainThread"]
            if len(non_main_threads):
                print
                print("Found {} background threads running:".format(len(non_main_threads)))
                for thread in non_main_threads:
                    print(" - " + thread.name)

        if hasattr(self.worker, "result"):
            element_id = self.worker.result.element_id
            robot_name = self.worker.result.robot_name
            return element_id, robot_name
        else:
            return None, None

