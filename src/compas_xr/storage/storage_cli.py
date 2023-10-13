import os
import sys
from compas_xr.storage.storage_interface import StorageInterface
import clr

#TODO: Find correct dependencies (these two for example)
lib_dir = os.path.join(os.path.dirname(__file__), "dependencies")
if lib_dir not in sys.path:
    sys.path.append(lib_dir)


#TODO: Find correct dependencies (these two for example)
clr.AddReference("Litedb.dll")
clr.AddReference("Firebase.dll")

# # Back up PROXY option, and works but not the ideal solution.
# from compas.rpc import Proxy

# class Storage(StorageInterface):
#     def __init__(self, config_file):
#         self.config_file = config_file

#     def download_file(self, path_on_cloud, path_local):
#         st = Proxy('compas_xr.storage.storage_proxy_api')
#         st.download_file(path_on_cloud, path_local, self.config_file)

#     def upload_file(self, path_on_cloud, path_local):
#         st = Proxy('compas_xr.storage.storage_proxy_api')
#         st.upload_file(path_on_cloud, path_local, self.config_file)
