import sys

if sys.platform == "cli":
    from compas_xr.storage.storage_cli import Storage
else:
    from compas_xr.storage.storage_pyrebase import Storage

__all__ = ["Storage"]
