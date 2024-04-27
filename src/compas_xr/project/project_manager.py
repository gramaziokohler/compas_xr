import os

from compas.data import json_dump
from compas.data import json_dumps
from compas.data import json_loads
from compas_timber.assembly import TimberAssembly

from compas_xr.project.assembly_extensions import AssemblyExtensions
from compas_xr.realtime_database import RealtimeDatabase
from compas_xr.storage import Storage


class ProjectManager(object):
    """
    The ProjectManager class is responsible for managing project specific data and operations that involve Firebase Storage and Realtime Database configuration.

    Parameters
    ----------
    config_path : str
        The path to the configuration file for the project.

    Attributes
    ----------
    storage : Storage
        The storage instance for the project.
    database : RealtimeDatabase
        The realtime database instance for the project.
    """

    def __init__(self, config_path):
        if not os.path.exists(config_path):
            raise Exception("Could not create Storage or Database with path {}!".format(config_path))
        self.storage = Storage(config_path)
        self.database = RealtimeDatabase(config_path)

    def application_settings_writer(
        self, project_name, storage_folder="None", obj_orientation=False
    ):
        """
        Uploads required application settings to the Firebase RealtimeDatabase.

        Parameters
        ----------
        project_name : str
            The name of the project where the app will look for information.
        storage_folder : str, optional
            The name of the storage folder, by default "None"
        obj_orientation : bool, optional
            The orientation of the object, by default False

        Returns
        -------
        None

        """
        data = {"parentname": project_name, "storagename": storage_folder, "objorientation": obj_orientation}
        self.database.upload_data(data, "ApplicationSettings")

    def upload_data_to_project(self, data, project_name, data_name):
        """
        Uploads data to the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        data : Any should be json serializable
            The data to be uploaded.
        project_name : str
            The name of the project under which the data will be stored.
        data_name : str
            The name of the child in which data will be stored.

        Returns
        -------
        None

        """
        self.database.upload_data_to_reference_as_child(data, project_name, data_name)

    def upload_project_data_from_compas(self, project_name, assembly, building_plan, qr_frames_list):
        """
        Formats data structure from Compas Class Objects and uploads them to the RealtimeDatabase in under the specified project name.

        Parameters
        ----------
        assembly : compas.datastructures.Assembly or compas_timber.assembly.TimberAssembly
            The assembly in which data will be extracted from.
        building_plan : compas_timber.planning.BuildingPlan
            The BuildingPlan in which data will be extracted from.
        qr_frames_list : list of compas.geometry.Frame
            List of frames at specific locations for application localization data.
        project_name : str
            The name of the project under which the data will be stored.

        Returns
        -------
        None

        """
        qr_assembly = AssemblyExtensions().create_qr_assembly(qr_frames_list)
        if isinstance(assembly, TimberAssembly):
            data = {
                "QRFrames": qr_assembly.__data__,
                "assembly": assembly.__data__,
                "beams": {beam.key: beam for beam in assembly.beams},
                "joints": {joint.key: joint for joint in assembly.joints},
                "building_plan": building_plan,
            }
        else:
            data = {
                "QRFrames": qr_assembly.__data__,
                "assembly": assembly.__data__,
                "parts": {part.key: part for part in assembly.parts()},
                "building_plan": building_plan,
            }
        self.database.upload_data(data, project_name)

    def upload_qr_frames_to_project(self, project_name, qr_frames_list):
        """
        Uploads QR Frames to the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        qr_frames_list : list of compas.geometry.Frame
            List of frames at specific locations for application localization data.
        project_name : str
            The name of the project under which the data will be stored.

        Returns
        -------
        None

        """
        qr_assembly = AssemblyExtensions().create_qr_assembly(qr_frames_list)
        data = qr_assembly.__data__
        self.database.upload_data_to_reference_as_child(data, project_name, "QRFrames")

    def upload_obj_to_storage(self, path_local, storage_folder_name):
        """
        Upload an .obj file to the Firebase Storage under the specified storage folder name.

        Parameters
        ----------
        file_path : str
            The path at which the obj file is stored.
        storage_folder_name : str
            The name of the storage folder where the .obj file will be uploaded.

        Returns
        -------
        None

        """
        storage_folder_list = ["obj_storage", storage_folder_name]
        self.storage.upload_file_as_bytes_to_deep_reference(path_local, storage_folder_list)

    def upload_objs_from_directory_to_storage(self, local_directory, storage_folder_name):
        """
        Uploads all .obj files from a directory to the Firebase Storage under the specified storage folder name.

        Parameters
        ----------
        directory_path : str
            The path to the directory where the projects .obj files are stored.
        storage_folder_name : str
            The name of the storage folder where the .obj files will be uploaded.

        Returns
        -------
        None

        """
        storage_folder_list = ["obj_storage", storage_folder_name]
        self.storage.upload_files_as_bytes_from_directory_to_deep_reference(local_directory, storage_folder_list)

    def get_project_data(self, project_name):
        """
        Retrieves data from the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        project_name : str
            The name of the project under which the data will be stored.

        Returns
        -------
        data : dict
            The data retrieved from the database at the point of fetching.

        """
        return self.database.get_data(project_name)

    def upload_assembly_to_storage(self, assembly, cloud_file_name, pretty=True):
        """
        Uploads an assembly to the Firebase Storage.

        Parameters
        ----------
        assembly : compas.datastructures.Assembly or compas_timber.assembly.TimberAssembly
            The assembly to be uploaded.
        cloud_file_name : str
            The name of the cloud file. Saved in JSON format, and needs to have a .json extension.

        Returns
        -------
        None

        """
        self.storage.upload_data(assembly, cloud_file_name, pretty=pretty)

    def get_assembly_from_storage(self, cloud_file_name):
        """
        Retrieves an assembly from the Firebase Storage.

        Parameters
        ----------
        cloud_file_name : str
            The name of the cloud file.

        Returns
        -------
        assembly : compas.datastructures.Assembly or compas_timber.assembly.TimberAssembly
            The assembly retrieved from the storage.

        """
        return self.storage.get_data(cloud_file_name)

    def edit_step_on_database(self, project_name, key, actor, is_built, is_planned, priority):
        """
        Edits a building plan step in the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        project_name : str
            The name of the project under which the data will be stored.
        key : str
            The key of the building plan step to be edited.
        actor : str
            The actor who will be performing the step.
        is_built : bool
            A boolean that determines if the step is built.
        is_planned : bool
            A boolean that determines if the step is planned.
        priority : int
            The priority of the step.

        Returns
        -------
        None

        """
        database_reference_list = [project_name, "building_plan", "data", "steps", key, "data"]
        current_data = self.database.get_data_from_deep_reference(database_reference_list)
        current_data["actor"] = actor
        current_data["is_built"] = is_built
        current_data["is_planned"] = is_planned
        current_data["priority"] = priority
        self.database.upload_data_to_deep_reference(current_data, database_reference_list)

    #TODO: visualize_project_data()
    #TODO: visualize_timbers_project_data()
    #TODO: Remove Below.

    # Functions for uploading Assemblies to the Database and Storage
    def upload_assembly_all_to_database(self, assembly, parentname): #TODO: REMOVE

        # Get data from the assembly
        data = assembly.__data__

        # Upload data using Database Class
        self.database.upload_data_all(data, parentname)

    def random_print(self):
        assembly_extensions = AssemblyExtensions()
        print("Hello World")

    # TODO: Integrated in toggle for removing joint keys.
    def upload_assembly_to_database(self, assembly, parentname, parentparamater, parameters, joints): #TODO: REMOVE

        # Get data from the assembly
        data = assembly.__data__

        # Create Data Structure form Assembly
        paramaters_nested = {}

        for param in parameters:
            values = data[parentparamater][param]
            parameters_dict = {param: values}
            paramaters_nested.update(parameters_dict)

        if joints == False:

            joint_keys = []
            elements = paramaters_nested[param]

            for item in elements:
                values = elements[item]
                if values["type"] == "joint":
                    joint_keys.append(item)

            for key in joint_keys:
                elements.pop(key)

        # Upload
        self.database.upload_data_all(paramaters_nested, parentname)

    def upload_assembly_aschild_to_database(self, assembly, parentname, childname, parentparameter, childparameter): #TODO: REMOVE

        # Get data from the assembly
        data = assembly.__data__

        # Get Assembly Information from Database
        assembly_info = data[parentparameter][childparameter]

        self.database.upload_data_aschild(assembly_info, parentname, childname)

    def upload_assembly_aschildren_to_database(
        self, assembly, parentname, childname, parentparameter, childparameter, parameters
    ):#TODO: REMOVE

        # Get data from the assembly
        data = assembly.__data__

        for param in parameters:
            values = data[parentparameter][childparameter][param]
            self.database.upload_data_aschildren(values, parentname, childname, param)

    # def upload_assembly_to_storage(self, path_on_cloud, assembly): #TODO: Keep

    #     # Turn Assembly to data
    #     data = json_dumps(assembly, pretty=True)  # TODO: json_dump vs json_dumps? ALSO Pretty can be false.

    #     # upload data to storage from the storage class method
    #     self.storage.upload_data(path_on_cloud, data)

    # Function for getting assemblies from Storage
    # def get_assembly_from_storage(self, path_on_cloud): #TODO: Keep

    #     data = self.storage.get_data(path_on_cloud)

    #     # TODO: I am not sure why, but when I use the get data, this needs to happen twice for it to return an assembly
    #     assembly = json_loads(data)

    #     return assembly
