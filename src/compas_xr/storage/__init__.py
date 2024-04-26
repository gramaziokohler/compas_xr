import sys

if sys.platform == "cli":
    from compas_xr.storage.storage_cli import Storage
else:
    from compas_xr.storage.storage_pyrebase import Storage

__all__ = ["Storage"]

if __name__ == "__main__":
    st = Storage(r"X:\GKR_working\Fall_2023\working_local\compas_xr_local\20240422_weeklyworking\python_library_updates\firebase_config\firebase_config.json")
    st.upload_file_from_bytes(r"C:\Users\josep\Downloads\24_vs.obj")
    # st.download_file("assembly_structure.json", r"X:\GKR_working\Fall_2023\git_working\compas_xr\data\assembly_structure_test.json")

    from compas.data import json_dumps
    # print(json_dumps(st))