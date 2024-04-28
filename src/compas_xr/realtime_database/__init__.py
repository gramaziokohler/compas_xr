import sys

if sys.platform == "cli":
    from compas_xr.realtime_database.realtime_database_cli import RealtimeDatabase
else:
    from compas_xr.realtime_database.realtime_database_pyrebase import RealtimeDatabase

__all__ = ["RealtimeDatabase"]