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
        sequence_id = value.get("sequence_id", None)
        response_id = value.get("response_id", None)
        device_id = value.get("device_id", None)
        time_stamp = value.get("time_stamp", None)

        if sequence_id is None or response_id is None or device_id is None or time_stamp is None:
            raise ValueError(
                "Information for Header parsing missing: sequence_id, response_id, device_id, or time_stamp."
            )
        instance = cls(
            increment_response_ID=False,
            sequence_id=sequence_id,
            response_id=response_id,
            device_id=device_id,
            time_stamp=time_stamp,
        )

        instance._update_sequence_counter_from_message(sequence_id)
        instance._update_response_id_from_message(response_id)

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
        header = header.data if header else Header(increment_response_ID=True).data
        self["header"] = header
        self["element_id"] = element_id
        self["robot_name"] = robot_name
        self["trajectory_id"] = "trajectory_id_" + str(element_id)

    @classmethod
    def parse(cls, value):
        """Parse the GetTrajectoryRequest message from the input value.
        Starts by parsing the header information and then the Message.
        """
        print("Here")
        print(str(value))
        try:
            header_info = value.get("header", None)
            print("1")
            if header_info is None:
                raise ValueError("Header Information is missing.")
            print("2")
            header = Header.parse(header_info)
            # header = None
            print("3")
            element_id = value.get("element_id", None)
            robot_name = value.get("robot_name", None)
            if element_id is None or robot_name is None:
                raise ValueError("Information for message parsing is missing: element_id or robot_name.")
            print("4")
            print(cls)
            instance = cls(element_id=element_id, robot_name=robot_name, header=header)
            print("Almost done")
            return instance
        except Exception as e:
            print("Error: " + str(e))
            return None


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

    def __init__(self, element_id, robot_name, robot_base_frame, trajectory, header=None):
        super(GetTrajectoryResult, self).__init__()
        header = header or Header()
        self["header"] = header.data
        self["element_id"] = element_id
        self["robot_name"] = robot_name
        self["robot_base_frame"] = robot_base_frame
        self["trajectory_id"] = "trajectory_id_" + str(element_id)
        self["trajectory"] = trajectory

    @classmethod
    def parse(cls, value):
        """Parse the GetTrajectoryResult message from the input value.
        Starts by parsing the header information and then the Message.
        """
        header_info = value.get("header", None)
        if header_info is None:
            raise ValueError("Header Information is missing.")
        header = Header.parse(header_info)

        element_id = value.get("element_id", None)
        trajectory = value.get("trajectory", None)
        robot_name = value.get("robot_name", None)
        robot_base_frame = value.get("robot_base_frame", None)
        if element_id is None or robot_name is None or robot_base_frame is None or trajectory is None:
            raise ValueError("Information for message parsing is missing: element_id, robot_name, or trajectory.")
        robot_base_frame = Frame.__from_data__(robot_base_frame)
        instance = cls(
            element_id=element_id,
            robot_name=robot_name,
            robot_base_frame=robot_base_frame,
            trajectory=trajectory,
            header=header,
        )
        return instance


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
        header = header or Header()
        self["header"] = header.data
        self["element_id"] = element_id
        self["robot_name"] = robot_name
        self["trajectory_id"] = "trajectory_id_" + str(element_id)
        self["trajectory"] = trajectory
        self["approval_status"] = approval_status

    @classmethod
    def parse(cls, value):
        """Parse the ApproveTrajectory message from the input value.
        Starts by parsing the header information and then the Message.
        """
        header_info = value.get("header", None)
        if header_info is None:
            raise ValueError("Header Information is missing.")
        header = Header.parse(header_info)

        element_id = value.get("element_id", None)
        trajectory = value.get("trajectory", None)
        robot_name = value.get("robot_name", None)
        approval_status = value.get("approval_status", None)
        if element_id is None or robot_name is None or trajectory is None or approval_status is None:
            raise ValueError(
                "Information for parsing is missing: element_id, robot_name, trajectory, or approval_status."
            )
        instance = cls(
            element_id=element_id,
            robot_name=robot_name,
            trajectory=trajectory,
            approval_status=approval_status,
            header=header,
        )
        return instance


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
        header = header or Header()
        self["header"] = header.data
        self["element_id"] = element_id
        self["trajectory_id"] = "trajectory_id_" + str(element_id)

    @classmethod
    def parse(cls, value):
        """Parse the ApprovalCounterRequest message from the input value.
        Starts by parsing the header information and then the Message.
        """
        header_info = value.get("header", None)
        if header_info is None:
            raise ValueError("Header Information is missing.")
        header = Header.parse(header_info)

        element_id = value.get("element_id", None)
        if element_id is None:
            raise ValueError("Information for message parsing is missing: element_id.")
        instance = cls(element_id=element_id, header=header)
        return instance


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
        header = header or Header()
        self["header"] = header.data
        self["element_id"] = element_id
        self["trajectory_id"] = "trajectory_id_" + str(element_id)

    @classmethod
    def parse(cls, value):
        """Parse the ApprovalCounterResult message from the input value.
        Starts by parsing the header information and then the Message.
        """
        header_info = value.get("header", None)
        if header_info is None:
            raise ValueError("Header Information is missing.")
        header = Header.parse(header_info)

        element_id = value.get("element_id", None)
        if element_id is None:
            raise ValueError("Information for message parsing is missing: element_id.")
        instance = cls(element_id=element_id, header=header)
        return instance


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
        header = header or Header()
        self["header"] = header.data
        self["element_id"] = element_id
        self["robot_name"] = robot_name
        self["trajectory_id"] = "trajectory_id_" + str(element_id)
        self["trajectory"] = trajectory

    @classmethod
    def parse(cls, value):
        """Parse the SendTrajectory message from the input value.
        Starts by parsing the header information and then the Message.
        """
        header_info = value.get("header", None)
        if header_info is None:
            raise ValueError("Header Information is missing.")
        header = Header.parse(header_info)

        element_id = value.get("element_id", None)
        trajectory = value.get("trajectory", None)
        robot_name = value.get("robot_name", None)
        if element_id is None or robot_name is None or trajectory is None:
            raise ValueError("Information for message parsing is missing: element_id, robot_name, or trajectory.")
        instance = cls(element_id=element_id, robot_name=robot_name, trajectory=trajectory, header=header)
        return instance
