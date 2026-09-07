import os
import sys

# On macOS/Linux, pythonnet defaults to Mono, but we want to use .NET Core (dotnet)
# if available, especially for Rhino 8+ development.
if sys.platform != "win32":
    os.environ["PYTHONNET_RUNTIME"] = "coreclr"

from pathlib import Path

import compas_pb
from compas_invocations2 import build
from compas_invocations2 import docs
from compas_invocations2 import grasshopper
from compas_invocations2 import mkdocs
from compas_invocations2 import style
from compas_invocations2 import tests
from compas_pb.invocations import create_class_assets
from compas_pb.invocations import create_proto_bundle
from compas_pb.invocations import generate_proto_classes
from invoke import Collection
from invoke import task


@task
def pre_build(ctx):
    """Generate the protobuf classes before building the package."""
    generate_proto_classes(ctx, target_language="python")


ns = Collection(
    docs.help,
    mkdocs.docs,
    style.check,
    style.lint,
    style.format,
    tests.test,
    tests.testdocs,
    build.prepare_changelog,
    build.clean,
    build.release,
    build.build_cpython_ghuser_components,
    grasshopper.yakerize,
    grasshopper.publish_yak,
    generate_proto_classes,
    create_class_assets,
    create_proto_bundle,
    pre_build,
)
ns.configure(
    {
        "base_folder": os.path.dirname(__file__),
        # compas_xr owns compas_xr.proto, so it publishes the schema bundle and the
        # generated bindings itself, the same way compas_pb does for the COMPAS types.
        "package_name": "compas_xr",
        "generated_folder": Path("./dist") / "generated",
        "proto_folder": Path("./src") / "compas_xr" / "proto",
        "proto_include_paths": [Path("./src") / "compas_xr" / "proto", compas_pb.PROTOBUF_DEFS],
        "proto_out_folder": Path("./src") / "compas_xr" / "proto",
        "ghuser_cpython": {
            "source_dir": "src/compas_xr/ghpython/components",
            "target_dir": "src/compas_xr/ghpython/components/ghuser",
        },
    }
)
