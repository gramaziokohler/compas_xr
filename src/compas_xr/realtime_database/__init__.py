import sys

if sys.platform == "cli":
    from compas_xr.realtime_database.realtime_database_cli import RealtimeDatabase
else:
    from compas_xr.realtime_database.realtime_database_pyrebase import RealtimeDatabase

__all__ = ["RealtimeDatabase"]

#TODO: REMOVE BELOW
# if __name__ == "__main__":
#     rd = RealtimeDatabase(r"X:\GKR_working\Fall_2023\working_local\compas_xr_local\20240422_weeklyworking\python_library_updates\firebase_config\firebase_config.json")
#     # db_ref = rd.construct_child_refrence("240325_TimbersDemo", "QRFrames")
#     db_ref = rd.construct_reference("Random_VS_test")

#     from compas.geometry import Frame
#     frame = Frame.worldXY()
#     frame_list = [frame.__data__, frame.__data__, frame.__data__]
    
#     static_dict = {
#     "key_1": 10,
#     "key_2": 20,
#     "key_3": 30,
#     "key_4": 40,
#     "key_5": 50
#     }

#     from compas.datastructures import Assembly
#     assembly = Assembly()
#     frame = Frame.worldXY()
#     frame2 = Frame.worldXY()
#     assembly.add_part(frame)
#     assembly.add_part(frame2)
    # print("assembly_data_type", type(assembly.__data__))
    # print("assembly_data", assembly.__data__)
    # from compas.data import json_dumps
    # print(json_dumps(assembly.__data__))
    # rd.upload_data_to_reference(frame_list, db_ref)

    # rd.upload_data_all(frame, "Random_VS_test_2")

    # from compas.data import json_dumps
    # print(json_dumps(st))
