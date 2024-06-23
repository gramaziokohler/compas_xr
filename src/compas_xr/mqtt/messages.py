import sys
import threading
import uuid
from datetime import datetime

from compas.geometry import Frame
from compas_eve import Message


class SequenceCounter(object):
    """An atomic, thread-safe sequence increament counter that increments with each message."""

    ROLLOVER_THRESHOLD = sys.maxsize

    def __init__(self, start=0):
        """Initialize a new counter to given initial value."""
        self._lock = threading.Lock()
        self._value = start

    def increment(self, num=1):
        """Atomically increment the counter by ``num`` and
        return the new value.
        """
        with self._lock:
            self._value += num
            if self._value > SequenceCounter.ROLLOVER_THRESHOLD:
                self._value = 1
            return self._value

    def update_from_msg(self, value):
        """Method to compare value received and current value
        if it is greater then current value update my current value.
        """
        with self._lock:
            if value > self._value:
                self._value = value


class ResponseID(object):
    """An atomic, thread-safe counter that increments with each service routine."""

    ROLLOVER_THRESHOLD = sys.maxsize

    def __init__(self, start=0):
        """Initialize a new counter to given initial value."""
        self._lock = threading.Lock()
        self._value = start

    def increment(self, num=1):
        """Atomically increment the counter by ``num`` and
        return the new value.
        """
        with self._lock:
            self._value += num
            if self._value > ResponseID.ROLLOVER_THRESHOLD:
                self._value = 1
            return self._value

    def update_from_msg(self, value):
        """Method to compare value received and current value
        if it is greater then current value update my current value.
        """
        with self._lock:
            if value > self._value:
                self._value = value


class Header(Message):
    """
    The header class is responsible for coordinating and understanding messages between users.

    The Header class provides methods for parsing, updating, and accessing the header fields of a message,
    and provides a means of defining attributes of the message in order to accept or ignore specific messages.

    Parameters
    ----------
    increment_response_ID : bool, optional
        Whether to increment the response ID when creating a new instance of Header.
    sequence_id : int, optional
        The sequence ID of the message. Optional for parsing.
    response_id : int, optional
        The response ID of the message. Optional for parsing.
    device_id : str, optional
        The device ID of the message. Optional for parsing.
    time_stamp : str, optional
        The timestamp of the message. Optional for parsing.

    Attributes
    ----------
    increment_response_ID : bool
        Whether to increment the response ID when creating a new instance of Header.
    sequence_id : int
        Sequence ID is an atomic counter that increments with each message.
    response_id : int
        Response ID is an int that increments with request routine.
    device_id : str
        Device ID coresponds to the unique system identifier that send the message.
    time_stamp : str
        Timestamp is the time in which the message was sent.
    """

    _shared_sequence_counter = None
    _shared_response_id_counter = None
    _device_id = None

    def __init__(
        self, increment_response_ID=False, sequence_id=None, response_id=None, device_id=None, time_stamp=None
    ):
        super(Header, self).__init__()
        self["sequence_id"] = sequence_id or self._ensure_sequence_id()
        self["response_id"] = response_id or self._ensure_response_id(increment_response_ID)
        self["device_id"] = device_id or self._get_device_id()
        self["time_stamp"] = time_stamp or self._get_time_stamp()

    @classmethod
    def parse(cls, value):
        """Parse the header information
        from the input value
        """
        instance = cls(value["sequence_id"], value["response_id"], value["device_id"], value["time_stamp"])
        instance._update_sequence_counter_from_message(value["sequence_id"])
        instance._update_response_id_from_message(value["response_id"])
        return instance

    def _get_device_id(self):
        """Ensure device ID is set and return it.
        If not set, generate a new device ID.
        """
        if not Header._device_id:
            Header._device_id = str(uuid.uuid4())
            self.device_id = Header._device_id
        else:
            self.device_id = Header._device_id
        return self.device_id

    def _get_time_stamp(self):
        """Generate timestamp and return it."""
        self.time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        return self.time_stamp

    def _ensure_sequence_id(self):
        """Ensure SequenceID is set and return it.
        If not set, generate new shared counter.
        """
        if not Header._shared_sequence_counter:
            Header._shared_sequence_counter = SequenceCounter()
            self.sequence_id = Header._shared_sequence_counter._value
        else:
            self.sequence_id = Header._shared_sequence_counter.increment()
        return self.sequence_id

    def _ensure_response_id(self, increment_response_ID=False):
        """Ensure ResponseID is set and return it.
        If not set, generate new shared counter.
        """
        if not Header._shared_response_id_counter:
            Header._shared_response_id_counter = ResponseID()
            self.response_id = Header._shared_response_id_counter._value
        else:
            if increment_response_ID:
                self.response_id = Header._shared_response_id_counter.increment()
                self.response_id = Header._shared_response_id_counter._value
            else:
                self.response_id = Header._shared_response_id_counter._value
        return self.response_id

    def _update_sequence_counter_from_message(self, sequence_id):
        """Update SequnceID Value if the message input is greater then
        current value +1. Used to ensure messages across devices are in sync
        upon receiving a message if device is restarted.
        """
        if Header._shared_sequence_counter is not None:
            Header._shared_sequence_counter.update_from_msg(sequence_id)
        else:
            Header._shared_sequence_counter = SequenceCounter(start=sequence_id)

    def _update_response_id_from_message(self, response_id):
        """Update ResponseID Value if the message input is greater then
        current value +1. Used to ensure messages across devices are in sync
        upon receiving a message if device is restarted.
        """
        if Header._shared_response_id_counter is not None:
            Header._shared_response_id_counter.update_from_msg(response_id)
        else:
            Header._shared_response_id_counter = ResponseID(start=response_id)

    def update_ids_from_message(self, sequence_id, response_id):
        """Update SequenceID and ResponseID values based on message inputs."""
        self._update_sequence_counter_from_message(sequence_id)
        self._update_response_id_from_message(response_id)


class GetTrajectoryRequest(Message):
    """
    The GetTrajectoryRequest class represents a request message from a user
    to the CAD for retrieving a trajectory.

    Parameters
    ----------
    element_id : str
        The ID of the element associated with the trajectory.
    robot_name : str
        The name of the robot associated with the trajectory.
    header : Header, optional
        The header object containing additional message information.

    Attributes
    ----------
    header : Header
        The header object containing additional message information.
    element_id : str
        The ID of the step in the BuildingPlan associated with the trajectory.
    robot_name : str
        The name of the robot associated with the trajectory.
    trajectory_id : str
        The ID of the trajectory. Default is "trajectory_id_" + str(element_id).
    """

    def __init__(self, element_id, robot_name, header=None, *args, **kwargs):
        super(GetTrajectoryRequest, self).__init__(*args, **kwargs)
        self["header"] = header or Header(increment_response_ID=True)
        self["element_id"] = element_id
        self["robot_name"] = robot_name
        self["trajectory_id"] = "trajectory_id_" + str(element_id)

    @classmethod
    def parse(cls, data):
        """Parse the GetTrajectoryRequest message from the input data.
        Starts by parsing the header information and then the Message.
        """
        return cls(data["element_id"], data["robot_name"], Header.parse(data["header"]))


class GetTrajectoryResult(Message):
    """
    The GetTrajectoryResult class represents a response message from the CAD
    to all active devices containing a retrieved trajectory.

    Parameters
    ----------
    element_id : str
        The ID of the element associated with the trajectory.
    robot_name : str
        The name of the robot associated with the trajectory.
    robot_base_frame : compas.geometry.Frame
        The base frame of the robot.
    trajectory : dict of joint names and joint values
        The retrieved trajectory.
    header : Header, optional
        The header object containing additional message information.

    Attributes
    ----------
    header : Header
        The header object containing additional message information.
    element_id : str
        The ID of the step in the BuildingPlan associated with the trajectory.
    robot_name : str
        The name of the robot associated with the trajectory.
    robot_base_frame : compas.geometry.Frame
        The base frame of the robot.
    trajectory_id : str
        The ID of the trajectory. Default is "trajectory_id_" + str(element_id).
    trajectory : dict of joint names and joint values
        The trajectory information computed for the request.
    """

    def __init__(self, element_id, robot_name, robot_base_frame, trajectory, pick_and_place=False, pick_index=None, end_effector_link_name=None, header=None):
        super(GetTrajectoryResult, self).__init__()
        self["header"] = header or Header()
        self["element_id"] = element_id
        self["robot_name"] = robot_name
        self["robot_base_frame"] = robot_base_frame
        self["trajectory_id"] = "trajectory_id_" + str(element_id)
        self["pick_and_place"] = pick_and_place
        self["pick_index"] = pick_index
        self["end_effector_link_name"] = end_effector_link_name
        self["trajectory"] = trajectory

    @classmethod
    def parse(cls, data):
        """Parse the GetTrajectoryResult message from the input data.
        Starts by parsing the header information and then the Message.
        """
        return cls(
            data["element_id"],
            data["robot_name"],
            Frame(**data["robot_base_frame"]),
            data["trajectory"],
            data["pick_and_place"],
            data["pick_index"],
            data["end_effector_link_name"],
            Header.parse(data["header"]),
        )


class ApproveTrajectory(Message):
    """
    The ApproveTrajectory class represents a response message between
    all active devices containing an approval decision for each user.

    Parameters
    ----------
    element_id : str
        The ID of the element associated with the trajectory.
    robot_name : str
        The name of the robot associated with the trajectory.
    trajectory : dict of joint names and joint values
        The approved trajectory.
    approval_status : int
        The approval status of the trajectory.
    header : Header, optional
        The header object containing additional message information.

    Attributes
    ----------
    header : Header
        The header object containing additional message information.
    element_id : str
        The ID of the step in the BuildingPlan associated with the trajectory.
    robot_name : str
        The name of the robot associated with the trajectory.
    trajectory_id : str
        The ID of the trajectory. Default is "trajectory_id_" + str(element_id).
    trajectory : dict of joint names and joint values
        The approved trajectory.
    approval_status : int
        The approval status of the trajectory.
        0: Not Approved, 1: Approved, 2: Consensus Approval, 3: Cancelation.
    """

    def __init__(self, element_id, robot_name, trajectory, approval_status, header=None):
        super(ApproveTrajectory, self).__init__()
        self["header"] = header or Header()
        self["element_id"] = element_id
        self["robot_name"] = robot_name
        self["trajectory_id"] = "trajectory_id_" + str(element_id)
        self["trajectory"] = trajectory
        self["approval_status"] = approval_status

    @classmethod
    def parse(cls, data):
        """Parse the ApproveTrajectory message from the input data.
        Starts by parsing the header information and then the Message.
        """
        return cls(
            data["element_id"],
            data["robot_name"],
            data["trajectory"],
            data["approval_status"],
            Header.parse(data["header"]),
        )


class ApprovalCounterRequest(Message):
    """
    The ApprovalCounterRequest class represents a request message from a single user
    to all active users to retrieve a count of all activie devices.

    Parameters
    ----------
    element_id : str
        The ID of the element associated with the approval counter.
    header : Header, optional
        The header object containing additional message information.

    Attributes
    ----------
    header : Header
        The header object containing additional message information.
    element_id : str
        The ID of the element associated with the approval counter.
    trajectory_id : str
        The ID of the trajectory. Default is "trajectory_id_" + str(element_id).
    """

    def __init__(self, element_id, header=None):
        super(ApprovalCounterRequest, self).__init__()
        self["header"] = header or Header()
        self["element_id"] = element_id
        self["trajectory_id"] = "trajectory_id_" + str(element_id)

    @classmethod
    def parse(cls, data):
        """Construct an object of this type from the provided data to support COMPAS JSON serialization.

        Parameters
        ----------
        data : dict
            The raw Python data representing the object.

        Returns
        -------
        object
        """
        return cls(data["element_id"], Header.parse(data["header"]))


class ApprovalCounterResult(Message):
    """
    The ApprovalCounterResult class represents a response message from all active devices
    containing to notify the primary device of the users listening.

    Parameters
    ----------
    element_id : str
        The ID of the element associated with the approval counter.
    header : Header, optional
        The header object containing additional message information.

    Attributes
    ----------
    header : Header
        The header object containing additional message information.
    element_id : str
        The ID of the element associated with the approval counter.
    trajectory_id : str
        The ID of the trajectory. Default is "trajectory_id_" + str(element_id).
    """

    def __init__(self, element_id, header=None):
        super(ApprovalCounterResult, self).__init__()
        self["header"] = header or Header()
        self["element_id"] = element_id
        self["trajectory_id"] = "trajectory_id_" + str(element_id)

    @classmethod
    def parse(cls, data):
        """Parse the ApprovalCounterResult message from the input data.
        Starts by parsing the header information and then the Message.
        """
        return cls(data["element_id"], Header.parse(data["header"]))


class SendTrajectory(Message):
    """
    The SendTrajectory class represents a message from a user to the CAD
    to give the Approval for Robotic Exacution.

    Parameters
    ----------
    element_id : str
        The ID of the element associated with the trajectory.
    robot_name : str
        The name of the robot associated with the trajectory.
    trajectory : dict of joint names and joint values
        The trajectory to be sent.
    header : Header, optional
        The header object containing additional message information.

    Attributes
    ----------
    header : Header
        The header object containing additional message information.
    element_id : str
        The ID of the element associated with the trajectory.
    robot_name : str
        The name of the robot associated with the trajectory.
    trajectory_id : str
        The ID of the trajectory. Default is "trajectory_id_" + str(element_id).
    trajectory : dict of joint names and joint values
        The trajectory to be sent.
    """

    def __init__(self, element_id, robot_name, trajectory, header=None):
        super(SendTrajectory, self).__init__()
        self["header"] = header or Header()
        self["element_id"] = element_id
        self["robot_name"] = robot_name
        self["trajectory_id"] = "trajectory_id_" + str(element_id)
        self["trajectory"] = trajectory

    @classmethod
    def parse(cls, data):
        """Parse the SendTrajectory message from the input data.
        Starts by parsing the header information and then the Message.
        """
        return cls(data["element_id"], data["robot_name"], data["trajectory"], Header.parse(data["header"]))
