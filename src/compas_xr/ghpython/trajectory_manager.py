class TrajectoryResultManager(object):
    trajectory = None
    requested_element_id = None
    robot_base_fame = None

    def ToString(self):
        return str(self)

    def __str__(self):
        return "Planning result for element {} with {} points".format(self.requested_element_id, len(self.trajectory.points))

    def format_trajectory(self, trajectory, robot_name):
        configs_dicts = []
        for point in trajectory.points:
            # Merge trajectory point with start config to make sure they are all full configurations
            # In the past, this was hardcoded only for the RFL, but it makes sense to do it for all
            point = trajectory.start_configuration.merged(point)
            joints_dict = point.joint_dict
            configs_dicts.append(joints_dict)
        return configs_dicts
