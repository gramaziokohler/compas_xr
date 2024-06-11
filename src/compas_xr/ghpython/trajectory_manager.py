from compas_robots import Configuration

class TrajectoryResultManager(object):
    trajectory = None
    requested_element_id = None
    robot_base_fame = None

    def ToString(self):
        return str(self)

    def __str__(self):
        return "Planning result for element {} with {} points".format(
            self.requested_element_id, len(self.trajectory.points)
        )

    def format_trajectory(self, trajectory, robot_name):
        configs_dicts = []
        for point in trajectory.points:
            if robot_name == "ETHZurichRFL":
                start_config = trajectory.start_configuration
                point = start_config.merged(point)
            joints_dict = point.joint_dict
            configs_dicts.append(joints_dict)
        return configs_dicts
