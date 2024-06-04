import os

from compas.geometry import Frame
from compas_timber.assembly import TimberAssembly
from compas_timber.planning import BuildingPlan
from compas_timber.planning import Step

from compas_xr.project.assembly_extensions import AssemblyExtensions
from compas_xr.realtime_database import RealtimeDatabase
from compas_xr.storage import Storage


class ProjectManager(object):
    """
    The ProjectManager class is responsible for managing project specific data and operations that involve
    Firebase Storage and Realtime Database configuration.

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

    def application_settings_writer(self, project_name, storage_folder="None", z_to_y_remap=False):
        """
        Uploads required application settings to the Firebase RealtimeDatabase.

        Parameters
        ----------
        project_name : str
            The name of the project where the app will look for information.
        storage_folder : str, optional
            The name of the storage folder, by default "None"
        z_to_y_remap : bool, optional
            The orientation of the object, if the obj was exported with z to y remap, by default False

        Returns
        -------
        None

        """
        data = {"project_name": project_name, "storage_folder": storage_folder, "z_to_y_remap": z_to_y_remap}
        self.database.upload_data(data, "ApplicationSettings")

    def create_project_data_from_compas(self, assembly, building_plan, qr_frames_list):
        """
        Formats data structure from Compas Class Objects.

        Parameters
        ----------
        assembly : compas.datastructures.Assembly or compas_timber.assembly.TimberAssembly
            The assembly in which data will be extracted from.
        building_plan : compas_timber.planning.BuildingPlan
            The BuildingPlan in which data will be extracted from.
        qr_frames_list : list of compas.geometry.Frame
            List of frames at specific locations for application localization data.

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
        return data

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
        Formats data structure from Compas Class Objects and uploads them to the RealtimeDatabase under project name.

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
        data = self.create_project_data_from_compas(assembly, building_plan, qr_frames_list)
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

    def upload_compas_object_to_storage(self, compas_object, cloud_file_name, pretty=True):
        """
        Uploads an assembly to the Firebase Storage.

        Parameters
        ----------
        compas_object : Any
            Any compas class instance that is serializable.
        cloud_file_name : str
            The name of the cloud file. Saved in JSON format, and needs to have a .json extension.

        Returns
        -------
        None

        """
        self.storage.upload_data(compas_object, cloud_file_name, pretty=pretty)

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

    def visualize_project_state_timbers(self, timber_assembly, project_name):
        """
        Retrieves and visualizes data from the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        timber_assembly : compas_timbers.assembly.TimberAssembly
            The assembly in which the project is based off of: Used for part visulization.
        project_name : str
            The name of the project under which the data will be stored.

        Returns
        -------
        last_built_index : int
            The index of the last built part in the project.
        step_locations : list of compas.geometry.Frame
            The locations of the building plan steps.
        built_human : list of compas_timber.beam.Blank
            The parts that have been built by a human.
        unbuilt_human : list of compas_timber.beam.Blank
            The parts that have not been built by a human.
        built_robot : list of compas_timber.beam.Blank
            The parts that have been built by a robot.
        unbuilt_robot : list of compas_timber.beam.Blank
            The parts that have not been built by a robot.

        """
        nodes = timber_assembly.graph.__data__["node"]
        buiding_plan_data_reference_list = [project_name, "building_plan", "data"]
        current_state_data = self.database.get_data_from_deep_reference(buiding_plan_data_reference_list)

        built_human = []
        unbuilt_human = []
        built_robot = []
        unbuilt_robot = []
        step_locations = []

        # Try to get the value for the last built index, if it doesn't exist make it null
        # TODO: This is a bit weird, but it will throw an error if I pass the last
        # TODO: built index to the BuildingPlan constructor
        if "LastBuiltIndex" in current_state_data:
            last_built_index = current_state_data["LastBuiltIndex"]
            current_state_data.pop("LastBuiltIndex")
        else:
            last_built_index = None

        building_plan = BuildingPlan.__from_data__(current_state_data)
        for step in building_plan.steps:
            step_data = step["data"]
            # Try to get the value for device_id, and if it exists remove it.
            if "device_id" in step_data:
                step_data.pop("device_id")
            step = Step.__from_data__(step["data"])
            step_locations.append(Frame.__from_data__(step.location))
            assembly_element_id = step.element_ids[0]
            # TODO: Tried to write like this, but find_by_key returns a NoneType object
            """
            part = timber_assembly.find_by_key(assembly_element_id)
            """
            part = nodes[assembly_element_id]["part"]
            if step.actor == "HUMAN":
                if step.is_built:
                    built_human.append(part.blank)
                else:
                    unbuilt_human.append(part.blank)
            else:
                if step.is_built:
                    built_robot.append(part.blank)
                else:
                    unbuilt_robot.append(part.blank)
        return last_built_index, step_locations, built_human, unbuilt_human, built_robot, unbuilt_robot

    def visualize_project_state(self, assembly, project_name):
        """
        Retrieves and visualizes data from the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        assembly : compas.datastructure.Assembly
            The assembly in which the project is based off of: Used for part visulization.
        project_name : str
            The name of the project under which the data is stored.

        Returns
        -------
        last_built_index : int
            The index of the last built part in the project.
        step_locations : list of compas.geometry.Frame
            The locations of the building plan steps.
        built_human : list of compas.datastructures.Part
            The parts that have been built by a human.
        unbuilt_human : list of compas.datastructures.Part
            The parts that have not been built by a human.
        built_robot : list of compas.datastructures.Part
            The parts that have been built by a robot.
        unbuilt_robot : list of compas.datastructures.Part
            The parts that have not been built by a robot.

        """
        buiding_plan_data_reference_list = [project_name, "building_plan", "data"]
        current_state_data = self.database.get_data_from_deep_reference(buiding_plan_data_reference_list)
        nodes = assembly.graph.__data__["node"]

        built_human = []
        unbuilt_human = []
        built_robot = []
        unbuilt_robot = []
        step_locations = []

        # Try to get the value for the last built index, if it doesn't exist make it null
        # TODO: This is a bit weird, but it will throw an error if I pass the last built index to the BuildingPlan
        if "LastBuiltIndex" in current_state_data:
            last_built_index = current_state_data["LastBuiltIndex"]
            current_state_data.pop("LastBuiltIndex")
        else:
            last_built_index = None
        if "PriorityTreeDictionary" in current_state_data:
            current_state_data.pop("PriorityTreeDictionary")


        building_plan = BuildingPlan.__from_data__(current_state_data)
        for step in building_plan.steps:
            step_data = step["data"]
            # Try to get the value for device_id, and if it exists remove it.
            if "device_id" in step_data:
                step_data.pop("device_id")
            step = Step.__from_data__(step["data"])
            step_locations.append(Frame.__from_data__(step.location))
            assembly_element_id = step.element_ids[0]
            part = nodes[assembly_element_id]["part"]

            if step.actor == "HUMAN":
                # TODO: I am not sure if this works in all scenarios of Part
                if step.is_built:
                    built_human.append(part)
                else:
                    unbuilt_human.append(part)
            else:
                if step.is_built:
                    built_robot.append(part)
                else:
                    unbuilt_robot.append(part)
        return last_built_index, step_locations, built_human, unbuilt_human, built_robot, unbuilt_robot
