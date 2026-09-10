import pytest

from compas_xr.mqtt.messages import GetTrajectoryRequest
from compas_xr.mqtt.messages import Header


def test_header_parse_preserves_every_field():
    """Header.parse used to pass values positionally into a signature whose first
    parameter is ``increment_response_ID``, shifting every field by one."""
    wire = {
        "sequence_id": 7,
        "response_id": 3,
        "device_id": "device-abc",
        "time_stamp": "2026-09-08T10:00:00",
    }

    header = Header.parse(wire)

    assert header["sequence_id"] == 7
    assert header["response_id"] == 3
    assert header["device_id"] == "device-abc"
    assert header["time_stamp"] == "2026-09-08T10:00:00"


def test_header_parse_keeps_zero_valued_counters():
    """sequence_id and response_id are counters that legitimately start at 0, which a
    falsiness check would discard and regenerate."""
    wire = {
        "sequence_id": 0,
        "response_id": 0,
        "device_id": "device-abc",
        "time_stamp": "2026-09-08T10:00:00",
    }

    header = Header.parse(wire)

    assert header["sequence_id"] == 0
    assert header["response_id"] == 0


@pytest.mark.parametrize("missing", ["sequence_id", "response_id", "device_id", "time_stamp"])
def test_header_parse_rejects_incomplete_headers(missing):
    wire = {
        "sequence_id": 1,
        "response_id": 2,
        "device_id": "device-abc",
        "time_stamp": "2026-09-08T10:00:00",
    }
    del wire[missing]

    with pytest.raises(ValueError, match=missing):
        Header.parse(wire)


def test_message_roundtrip_preserves_header():
    request = GetTrajectoryRequest(element_id="elem-7", robot_name="ur10e")

    parsed = GetTrajectoryRequest.parse(request.data)

    assert parsed["element_id"] == "elem-7"
    assert parsed["robot_name"] == "ur10e"
    for key in ("sequence_id", "response_id", "device_id", "time_stamp"):
        assert parsed["header"][key] == request["header"][key]
