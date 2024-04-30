from compas_robots import Configuration

RFL_ZERO_CONFIG = {
    "joint_values": [
        0,
        21.201999999999998,
        0,
        -7.4119999999999999,
        -2.96,
        0,
        0,
        0,
        0,
        0,
        0,
        -2.96,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -7.4119999999999999,
        -2.96,
        0,
        0,
        0,
        0,
        0,
        0,
        -2.96,
        0,
        0,
        0,
        0,
        0,
        0,
    ],
    "joint_names": [
        "bridge1_joint_EA_X",
        "bridge2_joint_EA_X",
        "robot11_joint_EA_Y",
        "robot12_joint_EA_Y",
        "robot11_joint_EA_Z",
        "robot11_joint_1",
        "robot11_joint_2",
        "robot11_joint_3",
        "robot11_joint_4",
        "robot11_joint_5",
        "robot11_joint_6",
        "robot12_joint_EA_Z",
        "robot12_joint_1",
        "robot12_joint_2",
        "robot12_joint_3",
        "robot12_joint_4",
        "robot12_joint_5",
        "robot12_joint_6",
        "robot21_joint_EA_Y",
        "robot22_joint_EA_Y",
        "robot21_joint_EA_Z",
        "robot21_joint_1",
        "robot21_joint_2",
        "robot21_joint_3",
        "robot21_joint_4",
        "robot21_joint_5",
        "robot21_joint_6",
        "robot22_joint_EA_Z",
        "robot22_joint_1",
        "robot22_joint_2",
        "robot22_joint_3",
        "robot22_joint_4",
        "robot22_joint_5",
        "robot22_joint_6",
    ],
    "joint_types": [
        2,
        2,
        2,
        2,
        2,
        0,
        0,
        0,
        0,
        0,
        0,
        2,
        0,
        0,
        0,
        0,
        0,
        0,
        2,
        2,
        2,
        0,
        0,
        0,
        0,
        0,
        0,
        2,
        0,
        0,
        0,
        0,
        0,
        0,
    ],
}


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
                zero_config = Configuration.__from_data__(RFL_ZERO_CONFIG)
                point = zero_config.merged(point)
            joints_dict = point.joint_dict
            configs_dicts.append(joints_dict)
        return configs_dicts
