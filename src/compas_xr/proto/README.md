# Protocol Buffer Definitions

This directory holds the wire schema for COMPAS XR's MQTT messages.

## Files

- `compas_xr.proto` — coordination header, joint trajectories, and the trajectory
  request/approval message set.

## Generating the Python bindings

```bash
invoke generate-proto-classes
```

**Generated files (`*_pb2.py`, `*_pb2.pyi`) are not committed.** Generate them after
cloning or after changing a `.proto`. Releases generate them in CI before publishing.

## Ownership

COMPAS XR owns these schemas, so it publishes both the `.proto` bundle and the generated
bindings for every supported language as release assets — the same way `compas_pb` does
for the COMPAS core types. Downstream runtimes such as the C# one pin a released version
and consume those bindings rather than regenerating from a git checkout.

## Integration with compas_pb

Messages import `compas_pb/generated/geometry.proto` so COMPAS geometry (such as the robot
base frame) travels as a typed `compas_pb.data.FrameData` rather than an untyped blob.
Registration with the `compas_pb` codec lives in `compas_xr/mqtt/conversions.py`.
