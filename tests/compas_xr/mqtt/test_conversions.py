"""Round-trip every MQTT message through the compas_pb protobuf codec."""

import pytest

from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Vector
from compas_pb import pb_dump_bts
from compas_pb import pb_load_bts

from compas_xr.mqtt import ApprovalCounterRequest
from compas_xr.mqtt import ApprovalCounterResult
from compas_xr.mqtt import ApproveTrajectory
from compas_xr.mqtt import GetTrajectoryRequest
from compas_xr.mqtt import GetTrajectoryResult
from compas_xr.mqtt import SendTrajectory
from compas_xr.mqtt.conversions import get_trajectory_request_from_pb
from compas_xr.mqtt.conversions import get_trajectory_request_to_pb
from compas_xr.mqtt.conversions import trajectory_from_pb
from compas_xr.mqtt.conversions import trajectory_to_pb

TRAJECTORY = {
    "points": [
        {"joint_names": ["j1", "j2"], "joint_values": [0.0, 1.5], "time_from_start": 0.0},
        {"joint_names": ["j1", "j2"], "joint_values": [0.5, 2.0], "time_from_start": 1.25},
    ]
}


def roundtrip(message):
    return pb_load_bts(pb_dump_bts(message))


def assert_header_survives(sent, received):
    for key in ("sequence_id", "response_id", "device_id", "time_stamp"):
        assert received["header"][key] == sent["header"][key]


def test_get_trajectory_request_roundtrip():
    sent = GetTrajectoryRequest(element_id="elem-7", robot_name="ur10e")

    received = roundtrip(sent)

    assert isinstance(received, GetTrajectoryRequest)
    assert received["element_id"] == "elem-7"
    assert received["robot_name"] == "ur10e"
    assert received["trajectory_id"] == "trajectory_id_elem-7"
    assert_header_survives(sent, received)


def test_get_trajectory_result_roundtrip():
    frame = Frame(Point(1, 2, 3), Vector.Xaxis(), Vector.Yaxis())
    sent = GetTrajectoryResult(
        element_id="elem-7",
        robot_name="ur10e",
        robot_base_frame=frame,
        trajectory=TRAJECTORY,
        pick_and_place=True,
        pick_index=2,
        end_effector_link_name="tool0",
    )

    received = roundtrip(sent)

    assert isinstance(received, GetTrajectoryResult)
    assert received["robot_base_frame"].point == frame.point
    assert received["pick_and_place"] is True
    assert received["pick_index"] == 2
    assert received["end_effector_link_name"] == "tool0"
    assert received["trajectory"] == TRAJECTORY
    assert_header_survives(sent, received)


def test_get_trajectory_result_allows_absent_optionals():
    sent = GetTrajectoryResult(
        element_id="elem-7",
        robot_name="ur10e",
        robot_base_frame=Frame.worldXY(),
        trajectory=TRAJECTORY,
    )

    received = roundtrip(sent)

    assert received["pick_and_place"] is False
    assert received["pick_index"] is None
    assert received["end_effector_link_name"] is None


def test_approve_trajectory_roundtrip():
    sent = ApproveTrajectory(
        element_id="elem-7",
        robot_name="ur10e",
        trajectory=TRAJECTORY,
        approval_status=2,
    )

    received = roundtrip(sent)

    assert isinstance(received, ApproveTrajectory)
    assert received["approval_status"] == 2
    assert received["trajectory"] == TRAJECTORY
    assert_header_survives(sent, received)


def test_approval_counter_messages_roundtrip():
    for message_type in (ApprovalCounterRequest, ApprovalCounterResult):
        sent = message_type(element_id="elem-7")

        received = roundtrip(sent)

        assert isinstance(received, message_type)
        assert received["element_id"] == "elem-7"
        assert received["trajectory_id"] == "trajectory_id_elem-7"
        assert_header_survives(sent, received)


def test_send_trajectory_roundtrip():
    sent = SendTrajectory(element_id="elem-7", robot_name="ur10e", trajectory=TRAJECTORY)

    received = roundtrip(sent)

    assert isinstance(received, SendTrajectory)
    assert received["trajectory"] == TRAJECTORY
    assert_header_survives(sent, received)


def test_trajectory_accepts_column_major_dict():
    """A planner may hand over {joint_name: [values per waypoint]}."""
    message = trajectory_to_pb({"j1": [0.0, 0.5], "j2": [1.5, 2.0]})

    assert trajectory_from_pb(message) == {
        "points": [
            {"joint_names": ["j1", "j2"], "joint_values": [0.0, 1.5]},
            {"joint_names": ["j1", "j2"], "joint_values": [0.5, 2.0]},
        ]
    }


def test_trajectory_accepts_objects_with_points():
    """compas_fab's JointTrajectory layout, matched structurally rather than imported."""

    class Point_:
        joint_names = ["j1"]
        joint_values = [0.25]
        time_from_start = None

    class Traj:
        points = [Point_()]

    assert trajectory_from_pb(trajectory_to_pb(Traj())) == {"points": [{"joint_names": ["j1"], "joint_values": [0.25]}]}


def test_empty_trajectory_roundtrips():
    assert trajectory_from_pb(trajectory_to_pb(None)) == {"points": []}


def test_conversions_are_registered_through_an_entry_point():
    """compas_pb discovers the conversions module itself, through the compas_pb.plugins
    entry point. Nothing in compas_xr should have to import it to make serialization work."""
    import sys

    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points

    registered = {ep.value for ep in entry_points(group="compas_pb.plugins")}

    assert "compas_xr.mqtt.conversions" in registered


def test_trajectory_id_survives_when_it_is_not_the_derived_value():
    """trajectory_id is on the wire, so it must come back off it. The constructors
    derive it from element_id, which would silently replace whatever the sender said."""
    sent = SendTrajectory(element_id="elem-7", robot_name="ur10e", trajectory=TRAJECTORY)
    sent["trajectory_id"] = "trajectory_id_from_a_different_scheme"

    received = roundtrip(sent)

    assert received["trajectory_id"] == "trajectory_id_from_a_different_scheme"


def test_trajectory_id_falls_back_to_the_derived_value():
    """An empty field on the wire means the sender never set one."""
    message = get_trajectory_request_to_pb(GetTrajectoryRequest(element_id="elem-7", robot_name="ur10e"))
    message.ClearField("trajectory_id")

    received = get_trajectory_request_from_pb(message)

    assert received["trajectory_id"] == "trajectory_id_elem-7"


@pytest.mark.parametrize(
    "names, values",
    [
        (["j1", "j2"], [0.0]),
        (["j1"], [0.0, 1.0]),
        ([], [0.0]),
    ],
)
def test_mismatched_point_is_rejected_before_serialization(names, values):
    trajectory = {"points": [{"joint_names": names, "joint_values": values}]}

    with pytest.raises(ValueError, match="Trajectory point 0"):
        trajectory_to_pb(trajectory)


def test_mismatched_point_error_names_the_offending_index():
    trajectory = {
        "points": [
            {"joint_names": ["j1", "j2"], "joint_values": [0.0, 1.0]},
            {"joint_names": ["j1", "j2"], "joint_values": [0.0, 1.0]},
            {"joint_names": ["j1", "j2"], "joint_values": [0.0]},
        ]
    }

    with pytest.raises(ValueError, match=r"Trajectory point 2 has 2 joint names but 1 joint values"):
        trajectory_to_pb(trajectory)
