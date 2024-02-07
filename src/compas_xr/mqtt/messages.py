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
        
    #TODO: Review This implementation. I am not sure if it will work properly or not. (Especially with the parse method)
    def update(self, value):
        """Determine by the input if it is the same as current value
        and if it is increment, otherwise set to the input value.
        """
        with self._lock:
            if value == self._value:
                self._increment()
            else:
                self._value = value
            return self._value
    
class Header(UserDict):
    """Message header object used for publishing and subscribing to/from topics for compas_XR.

    A message header is fundamentally a dictionary and behaves as one."""
    _shared_sequence_counter = None
    _shared_response_id_counter = None
    _last_response_id = None

    def __init__(self):
        # super(Header, self).__init__()
        self.sequence_id = self._ensure_sequence_id()    
        self.response_id = self._ensure_response_id()
        self.device_id = self._get_device_id() #TODO: I THINK THIS CAN BE SIMPLIFIED.
        self.time_stamp = self._get_time_stamp() #TODO: I THINK THIS CAN BE SIMPLIFIED.

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data.get(name, None)

    @classmethod
    def parse(cls, value):
        instance = cls()
        instance.update(value)
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
    
    #TODO: Check Implementation.
    def _ensure_response_id(self):
        if not Header._shared_response_id_counter:
            Header._shared_response_id_counter = ResponseID()
            self.response_id = Header._shared_response_id_counter._value
            Header._last_response_id = self.response_id
        else:
            if Header._last_response_id != Header._shared_response_id_counter._value:
                Header._shared_response_id_counter._value = self.response_id
                self.response_id = Header._shared_response_id_counter._value
                Header._last_response_id = self.response_id
            else:
                self.response_id = Header._shared_response_id_counter.increment()
                Header._last_response_id = self.response_id
        return self.response_id
    
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

    def __init__(self, element_id):
        # super(GetTrajectoryRequest, self).__init__()
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
        # super(ApproveTrajectory, self).__init__()
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

class ApprovalCounterResult(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, element_id):
        # super(ApproveTrajectory, self).__init__()
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