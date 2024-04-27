"""
Background Task component.

Executes a long-running task in the background, while keeping Grasshopper reactive.

COMPAS EVE v0.3.4
"""

import threading
import scriptcontext as sc

from compas_eve.ghpython import BackgroundWorker
from ghpythonlib.componentbase import executingcomponent as component


DEBUG = False


class BackgroundTaskComponent(component):
    def RunScript(self, reset, task, on):
        if not on:
            BackgroundWorker.stop_instance_by_component(ghenv)  # noqa: F821
            return None

        self.worker = BackgroundWorker.instance_by_component(ghenv, task, force_new=reset)  # noqa: F821

        if not self.worker.is_working() and not self.worker.is_done() and reset:
            self.worker.start_work()

        print("Worker ID: {}".format(id(self.worker)))
        print("Is worker running? {}".format(self.worker.is_working()))
        print("Worker completed? {}".format(self.worker.is_done()))
        if hasattr(self.worker, "thread"):
            print("Worker thread: {}".format(self.worker.thread))

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
            return self.worker.result
        else:
            return None
