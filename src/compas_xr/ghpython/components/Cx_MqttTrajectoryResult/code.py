"""
Sync Results.

The Sync Result component is used to consolidate all user-defined inputs for the resulting trajectory and coordinate them into a single, unified trajectory.

COMPAS XR v0.8.0
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_xr.ghpython import TrajectoryResultManager


class SyncResultComponent(component):
    def RunScript(self, element_id, trajectory, robot_base_frame, pick_and_place, pick_index, ee_link_name, options):
        if element_id:
            result = TrajectoryResultManager()
            result.requested_element_id = element_id
            result.robot_base_frame = robot_base_frame
            result.trajectory = result.format_trajectory(trajectory)
            if pick_and_place != None:
                result.pick_and_place = pick_and_place
                if pick_and_place:
                    result.pick_index = pick_index
                    result.end_effector_link_name = ee_link_name
            else:
                result.pick_and_place = False
        else:
            result = None
