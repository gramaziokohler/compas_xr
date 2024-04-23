import sys

if sys.platform == "cli":
    from compas_xr.realtime_database.realtime_database_cli import RealtimeDatabase
else:
    from compas_xr.realtime_database.realtime_database_pyrebase import RealtimeDatabase

__all__ = ["RealtimeDatabase"]

if __name__ == "__main__":
    rd = RealtimeDatabase(r"X:\GKR_working\Fall_2023\working_local\compas_xr_local\20240422_weeklyworking\python_library_updates\firebase_config\firebase_config.json")
    rd.construct_reference("Random")

    # from compas.data import json_dumps
    # print(json_dumps(st))
