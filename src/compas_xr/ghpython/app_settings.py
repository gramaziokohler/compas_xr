class AppSettings(object):

    def __init__(self, project_name, storage_folder=None, z_to_y_remap=None):
        self.project_name = project_name
        self.storage_folder = storage_folder or "None"
        self.z_to_y_remap = z_to_y_remap or False

    def ToString(self):
        return str(self)

    def __str__(self):
        return "AppSettings, project_name={}, storage_folder={}, z_to_y_remap={}".format(self.project_name, self.storage_folder, self.z_to_y_remap)

    def __data__(self):
        return {
            "project_name": self.project_name,
            "storage_folder": self.storage_folder,
            "z_to_y_remap": self.z_to_y_remap,
        }
