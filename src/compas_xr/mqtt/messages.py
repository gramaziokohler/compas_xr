import threading
import uuid
from datetime import datetime

# Python 2/3 compatibility import list
try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict


class SequenceCounter(object):
    """An atomic, thread-safe sequence increament counter."""
    ROLLOVER_THRESHOLD = 1000000

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
    """An atomic, thread-safe sequence increament counter."""
    ROLLOVER_THRESHOLD = 1000000

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
    
class Header(UserDict):
    """Message header object used for publishing and subscribing to/from topics for compas_XR.

    A message header is fundamentally a dictionary and behaves as one."""
    _shared_sequence_counter = None
    _shared_response_id_counter = None

    def __init__(self, increment_response_ID=False, sequence_id=None, response_id=None, device_id=None, time_stamp=None):
        # super(Header, self).__init__()
        self.sequence_id = sequence_id if sequence_id else self._ensure_sequence_id()    
        self.response_id = response_id if response_id else self._ensure_response_id(increment_response_ID)
        self.device_id = device_id if device_id else self._get_device_id()
        self.time_stamp = time_stamp if time_stamp else self._get_time_stamp()

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data.get(name, None)

    @classmethod
    def parse(cls, value):
        sequence_id = value.get("sequence_id", None)
        response_id = value.get("response_id", None)
        device_id = value.get("device_id", None)
        time_stamp = value.get("time_stamp", None)

        #If any of the required fields are missing raise an error.
        if sequence_id is None or response_id is None or device_id is None or time_stamp is None:
            raise ValueError("One or more required fields are missing.")
        instance = cls(increment_response_ID=False, sequence_id=sequence_id, response_id=response_id, device_id=device_id, time_stamp=time_stamp)

        #Update the sequence counter and response id from the message received.
        cls._update_sequence_counter_from_message(instance, sequence_id)
        cls._update_response_id_from_message(instance, response_id)
        
        return instance
    
    def _get_device_id(self):
        self.device_id = str(uuid.uuid4())
        return self.device_id

    def _get_time_stamp(self):
        self.time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        return self.time_stamp
    
    def _ensure_sequence_id(self):
        if not Header._shared_sequence_counter:
            Header._shared_sequence_counter = SequenceCounter()
            self.sequence_id = Header._shared_sequence_counter._value
        else:
            self.sequence_id = Header._shared_sequence_counter.increment()
        return self.sequence_id
    
    #TODO: Check Implementation... should only increment for GetTrajectoryRequest.
    def _ensure_response_id(self, increment_response_ID=False):
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
    
    #TODO: Check Implementation... should update the value of my shared SequenceCounter value if it parses a message where it is greater then the one I have.
    def _update_sequence_counter_from_message(self, sequence_id):
        if Header._shared_sequence_counter is not None:
            Header._shared_sequence_counter.update_from_msg(sequence_id)
        else:
            Header._shared_sequence_counter = SequenceCounter(start=sequence_id)
    
    #TODO: Check Implementation... should update the value of my shared responseIDCounter value if it parses a message where it is greater then the one I have.
    def _update_response_id_from_message(self, response_id):
        if Header._shared_response_id_counter is not None:
            Header._shared_response_id_counter.update_from_msg(response_id)
        else:
            Header._shared_response_id_counter = ResponseID(start=response_id)

    @property
    def data(self):
        return {
            "sequence_id": self.sequence_id,
            "response_id": self.response_id,
            "device_id": self.device_id,
            "time_stamp": self.time_stamp,
        }
    
class GetTrajectoryRequest(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, element_id, header=None): #TODO: I GET A NONE TYPE ERROR IN THIS METHOD, AND I AM NOT SURE WHY
        # super(GetTrajectoryRequest, self).__init__()
        if header is not None:
            self.header=header
        else:
            self.header = Header(increment_response_ID=True)
        self.element_id = element_id
        self.trajectory_id = "trajectory_id_" + str(element_id)

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data.get(name, None)

    @classmethod
    def parse(cls, value): #TODO: I GET A NONE TYPE ERROR IN THIS METHOD, AND I AM NOT SURE WHY
        # Parse the header separately
        header_info = value.get("header", None)
        if header_info is None:
            raise ValueError("Header information is missing.")
        header = Header.parse(header_info)

        # Retrieve other required values from the input value
        element_id = value.get("element_id", None)
        if element_id is None:
            raise ValueError("element_id information is missing.")
        # Create an instance of the class with the retrieved values and the provided header
        instance = cls(element_id=element_id, header=header)

        return instance
    
    @property
    def data(self):
        return {
            "header": self.header.data,
            "element_id": self.element_id,
            "trajectory_id": self.trajectory_id,
        }
    
class GetTrajectoryResult(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, element_id, trajectory):
        # super(GetTrajectoryResult, self).__init__()
        self.header = Header()
        self.element_id = element_id
        self.trajectory_id = "trajectory_id_" + str(element_id)
        self.trajectory = trajectory

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data.get(name, None)

    @classmethod
    def parse(cls, value):
        #TODO: Should this throw an exception if the items are not there is not in the value or will this produce the error?
        instance = cls(value.get("element_id", None), value.get("trajectory", None))
        instance.update(value)
        #TODO: THIS IS A NEW IMPLEMENTATION AND NEEDS TO BE TESTED
        return instance
    
    @property
    def data(self):
        return {
            "header": self.header.data,
            "element_id": self.element_id,
            "trajectory_id": self.trajectory_id,
            "trajectory": self.trajectory,
        }
    
class ApproveTrajectory(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, element_id, trajectory, approval_status):
        # super(ApproveTrajectory, self).__init__()
        self.header = Header()
        self.element_id = element_id
        self.trajectory_id = "trajectory_id_" + str(element_id)
        self.trajectory = trajectory
        self.approval_status = approval_status

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data.get(name, None)

    @classmethod
    def parse(cls, value):
        #TODO: Should this throw an exception if the items are not there is not in the value or will this produce the error?
        instance = cls(value.get("element_id", None), value.get("trajectory", None), value.get("approval_status", None))
        instance.update(value)
        #TODO: THIS IS A NEW IMPLEMENTATION AND NEEDS TO BE TESTED
        return instance
    
    @property
    def data(self):
        return {
            "header": self.header.data,
            "element_id": self.element_id,
            "trajectory_id": self.trajectory_id,
            "trajectory": self.trajectory,
            "approval_status": self.approval_status,
        }

class ApprovalCounterRequest(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, element_id):
        # super(ApprovalCounterRequest, self).__init__()
        self.header = Header()
        self.element_id = element_id
        self.trajectory_id = "trajectory_id_" + str(element_id)

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data.get(name, None)

    @classmethod
    def parse(cls, value):
        #TODO: Should this throw an exception if the items are not there is not in the value or will this produce the error?
        instance = cls(value.get("element_id", None))
        instance.update(value)
        #TODO: THIS IS A NEW IMPLEMENTATION AND NEEDS TO BE TESTED
        return instance
    
    @property
    def data(self):
        return {
            "header": self.header.data,
            "element_id": self.element_id,
            "trajectory_id": self.trajectory_id,
        }

class ApprovalCounterResult(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, element_id):
        # super(ApprovalCounterResult, self).__init__()
        self.header = Header()
        self.element_id = element_id
        self.trajectory_id = "trajectory_id_" + str(element_id)

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data.get(name, None)

    @classmethod
    def parse(cls, value):
        #TODO: Should this throw an exception if the items are not there is not in the value or will this produce the error?
        instance = cls(value.get("element_id", None))
        instance.update(value)
        return instance
    
    @property
    def data(self):
        return {
            "header": self.header.data,
            "element_id": self.element_id,
            "trajectory_id": self.trajectory_id,
        }
    
class SendTrajectory(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, element_id, trajectory):
        # super(SendTrajectory, self).__init__()
        self.header = Header()
        self.element_id = element_id
        self.trajectory_id = "trajectory_id_" + str(element_id)
        self.trajectory = trajectory

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data.get(name, None)

    @classmethod
    def parse(cls, value):
        #TODO: Should this throw an exception if the items are not there is not in the value or will this produce the error?
        instance = cls(value.get("element_id", None), value.get("trajectory", None))
        instance.update(value)
        return instance
    
    @property
    def data(self):
        return {
            "header": self.header.data,
            "element_id": self.element_id,
            "trajectory_id": self.trajectory_id,
            "trajectory": self.trajectory,
        }