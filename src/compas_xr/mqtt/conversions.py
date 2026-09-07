"""Registers the COMPAS XR MQTT messages with the ``compas_pb`` codec.

COMPAS XR owns ``compas_xr.proto``, so it also owns the mapping between the generated
protobuf classes and the message classes in :mod:`compas_xr.mqtt.messages`. The
``compas_pb`` runtime contains no reference to COMPAS XR; the two meet at the registry.

Nothing imports this module explicitly. It is declared as a ``compas_pb.plugins`` entry
point in ``pyproject.toml``, and ``compas_pb`` imports it for its side effects the first
time it serializes anything.
"""

from compas_pb.conversions import frame_from_pb
from compas_pb.conversions import frame_to_pb
from compas_pb.registry import pb_deserializer
from compas_pb.registry import pb_serializer

from compas_xr.mqtt.messages import ApprovalCounterRequest
from compas_xr.mqtt.messages import ApprovalCounterResult
from compas_xr.mqtt.messages import ApproveTrajectory
from compas_xr.mqtt.messages import GetTrajectoryRequest
from compas_xr.mqtt.messages import GetTrajectoryResult
from compas_xr.mqtt.messages import Header
from compas_xr.mqtt.messages import SendTrajectory
from compas_xr.proto import compas_xr_pb2 as pb

__all__ = [
    "trajectory_to_pb",
    "trajectory_from_pb",
]


# ============================================================================
# Header
# ============================================================================


def _header_to_pb(header):
    return pb.Header(
        sequence_id=header["sequence_id"],
        response_id=header["response_id"],
        device_id=header["device_id"],
        time_stamp=header["time_stamp"],
    )


def _header_from_pb(message):
    return Header(
        sequence_id=message.sequence_id,
        response_id=message.response_id,
        device_id=message.device_id,
        time_stamp=message.time_stamp,
    )


# ============================================================================
# Trajectories
# ============================================================================


def _iter_points(trajectory):
    """Yield ``(joint_names, joint_values, time_from_start)`` for each waypoint.

    Trajectories reach COMPAS XR from whichever planning service the project plugs in,
    so three shapes are accepted:

    1. An object exposing ``points``, each with ``joint_names`` / ``joint_values`` and an
       optional ``time_from_start`` — this is the ``compas_fab`` JointTrajectory layout,
       matched structurally so COMPAS XR does not need to depend on ``compas_fab``.
    2. A sequence of mappings using those same keys.
    3. A mapping of joint name to a sequence of values, one entry per waypoint.

    Shape 3 is transposed into waypoints. Deserialization always returns shape 2, which
    is the canonical form going forward.
    """
    points = getattr(trajectory, "points", None)

    if points is None and isinstance(trajectory, dict) and "points" in trajectory:
        points = trajectory["points"]

    if points is not None:
        for point in points:
            yield (
                list(_get(point, "joint_names") or []),
                [float(value) for value in (_get(point, "joint_values") or [])],
                _time_from_start(point),
            )
        return

    if isinstance(trajectory, dict):
        # Column-major: {joint_name: [v0, v1, ...]}
        names = list(trajectory)
        columns = [list(trajectory[name]) for name in names]
        for values in zip(*columns) if columns else []:
            yield names, [float(value) for value in values], None
        return

    raise TypeError("Unsupported trajectory shape: {!r}".format(type(trajectory)))


def _get(point, key):
    if isinstance(point, dict):
        return point.get(key)
    return getattr(point, key, None)


def _time_from_start(point):
    value = _get(point, "time_from_start")
    if value is None:
        return None
    # compas_fab exposes a Duration object rather than a plain number.
    seconds = getattr(value, "seconds", None)
    if seconds is not None:
        nanoseconds = getattr(value, "nanoseconds", 0) or 0
        return float(seconds) + float(nanoseconds) / 1e9
    return float(value)


def trajectory_to_pb(trajectory):
    """Convert a planner trajectory into a :class:`compas_xr.v1.JointTrajectory`."""
    message = pb.JointTrajectory()
    if trajectory is None:
        return message

    for joint_names, joint_values, time_from_start in _iter_points(trajectory):
        point = message.points.add()
        point.joint_names.extend(joint_names)
        point.joint_values.extend(joint_values)
        if time_from_start is not None:
            point.time_from_start = time_from_start
    return message


def trajectory_from_pb(message):
    """Convert a :class:`compas_xr.v1.JointTrajectory` into the canonical dict form."""
    points = []
    for point in message.points:
        entry = {
            "joint_names": list(point.joint_names),
            "joint_values": list(point.joint_values),
        }
        if point.HasField("time_from_start"):
            entry["time_from_start"] = point.time_from_start
        points.append(entry)
    return {"points": points}


# ============================================================================
# GetTrajectoryRequest
# ============================================================================


@pb_serializer(GetTrajectoryRequest)
def get_trajectory_request_to_pb(message):
    return pb.GetTrajectoryRequest(
        header=_header_to_pb(message["header"]),
        element_id=message["element_id"],
        robot_name=message["robot_name"],
        trajectory_id=message["trajectory_id"],
    )


@pb_deserializer(pb.GetTrajectoryRequest)
def get_trajectory_request_from_pb(message):
    return GetTrajectoryRequest(
        element_id=message.element_id,
        robot_name=message.robot_name,
        header=_header_from_pb(message.header),
    )


# ============================================================================
# GetTrajectoryResult
# ============================================================================


@pb_serializer(GetTrajectoryResult)
def get_trajectory_result_to_pb(message):
    result = pb.GetTrajectoryResult(
        header=_header_to_pb(message["header"]),
        element_id=message["element_id"],
        robot_name=message["robot_name"],
        trajectory_id=message["trajectory_id"],
        trajectory=trajectory_to_pb(message["trajectory"]),
        pick_and_place=bool(message["pick_and_place"]),
    )
    if message["robot_base_frame"] is not None:
        result.robot_base_frame.CopyFrom(frame_to_pb(message["robot_base_frame"]))
    if message["pick_index"] is not None:
        result.pick_index = message["pick_index"]
    if message["end_effector_link_name"] is not None:
        result.end_effector_link_name = message["end_effector_link_name"]
    return result


@pb_deserializer(pb.GetTrajectoryResult)
def get_trajectory_result_from_pb(message):
    return GetTrajectoryResult(
        element_id=message.element_id,
        robot_name=message.robot_name,
        robot_base_frame=frame_from_pb(message.robot_base_frame) if message.HasField("robot_base_frame") else None,
        trajectory=trajectory_from_pb(message.trajectory),
        pick_and_place=message.pick_and_place,
        pick_index=message.pick_index if message.HasField("pick_index") else None,
        end_effector_link_name=(message.end_effector_link_name if message.HasField("end_effector_link_name") else None),
        header=_header_from_pb(message.header),
    )


# ============================================================================
# ApproveTrajectory
# ============================================================================


@pb_serializer(ApproveTrajectory)
def approve_trajectory_to_pb(message):
    return pb.ApproveTrajectory(
        header=_header_to_pb(message["header"]),
        element_id=message["element_id"],
        robot_name=message["robot_name"],
        trajectory_id=message["trajectory_id"],
        trajectory=trajectory_to_pb(message["trajectory"]),
        approval_status=message["approval_status"],
    )


@pb_deserializer(pb.ApproveTrajectory)
def approve_trajectory_from_pb(message):
    return ApproveTrajectory(
        element_id=message.element_id,
        robot_name=message.robot_name,
        trajectory=trajectory_from_pb(message.trajectory),
        approval_status=message.approval_status,
        header=_header_from_pb(message.header),
    )


# ============================================================================
# ApprovalCounterRequest / ApprovalCounterResult
# ============================================================================


@pb_serializer(ApprovalCounterRequest)
def approval_counter_request_to_pb(message):
    return pb.ApprovalCounterRequest(
        header=_header_to_pb(message["header"]),
        element_id=message["element_id"],
        trajectory_id=message["trajectory_id"],
    )


@pb_deserializer(pb.ApprovalCounterRequest)
def approval_counter_request_from_pb(message):
    return ApprovalCounterRequest(
        element_id=message.element_id,
        header=_header_from_pb(message.header),
    )


@pb_serializer(ApprovalCounterResult)
def approval_counter_result_to_pb(message):
    return pb.ApprovalCounterResult(
        header=_header_to_pb(message["header"]),
        element_id=message["element_id"],
        trajectory_id=message["trajectory_id"],
    )


@pb_deserializer(pb.ApprovalCounterResult)
def approval_counter_result_from_pb(message):
    return ApprovalCounterResult(
        element_id=message.element_id,
        header=_header_from_pb(message.header),
    )


# ============================================================================
# SendTrajectory
# ============================================================================


@pb_serializer(SendTrajectory)
def send_trajectory_to_pb(message):
    return pb.SendTrajectory(
        header=_header_to_pb(message["header"]),
        element_id=message["element_id"],
        robot_name=message["robot_name"],
        trajectory_id=message["trajectory_id"],
        trajectory=trajectory_to_pb(message["trajectory"]),
    )


@pb_deserializer(pb.SendTrajectory)
def send_trajectory_from_pb(message):
    return SendTrajectory(
        element_id=message.element_id,
        robot_name=message.robot_name,
        trajectory=trajectory_from_pb(message.trajectory),
        header=_header_from_pb(message.header),
    )
