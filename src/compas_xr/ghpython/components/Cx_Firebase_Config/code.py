"""
Settings for Firebase.

COMPAS XR v0.8.0
"""

import os
import json

from compas_xr.ghpython.firebase_config import FirebaseConfig

from ghpythonlib.componentbase import executingcomponent as component


class FirebaseConfigComponent(component):
    def RunScript(self, filepath, filename, api_key, auth_domain, database_url, storage_bucket):

        if not (api_key and auth_domain and database_url and storage_bucket):
            self.Message = "You are missing some config information"
            raise Exception("Missing Config Info")

        config_path = None
        firebase_config = FirebaseConfig(api_key, auth_domain, database_url, storage_bucket)
        config = firebase_config.__data__()

        if config and filepath:
            if os.path.exists(filepath):
                if not filename:
                    filename = os.path.join(filepath, "firebase_config.json")
                if filename:
                    filename = os.path.join(filepath, filename)

                config = dict(config)
                with open(filename, "w") as f:
                    json.dump(config, f)
                config_path = filename
                self.Message = "Config Written"
            else:
                self.Message = "You filepath does not exist"
                raise Exception("Path does not exist {}".format(filepath))
        else:
            self.Message = "You are missing your filepath"
            raise Exception("Missing Filepath")

        return config_path
