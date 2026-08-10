import os
from typing import Any

from compas.geometry import Box
from compas.geometry import Frame
from compas_model.models import Model
from compas_timber.model import TimberModel
from compas_timber.planning import BuildingPlan
from compas_timber.planning import Step

from compas_xr.project.model_extensions import ModelExtensions
from compas_xr.realtime_database import RealtimeDatabase
from compas_xr.storage import Storage


class ProjectManager:
    """
    The ProjectManager class is responsible for managing project specific data and operations that involve
    Firebase Storage and Realtime Database configuration.

    Parameters
    ----------
    config_path
        The path to the configuration file for the project.

    Attributes
    ----------
    storage : Storage
        The storage instance for the project.
    database : RealtimeDatabase
        The realtime database instance for the project.
    """

    def __init__(self, config_path: str):
        if not os.path.exists(config_path):
            raise Exception("Could not create Storage or Database with path {}!".format(config_path))
        self.storage = Storage(config_path)
        self.database = RealtimeDatabase(config_path)

    def application_settings_writer(self, project_name: str, storage_folder: str = "None", z_to_y_remap: bool = False) -> None:
        """
        Uploads required application settings to the Firebase RealtimeDatabase.

        Parameters
        ----------
        project_name
            The name of the project where the app will look for information.
        storage_folder
            The name of the storage folder.
        z_to_y_remap
            The orientation of the object, if the obj was exported with z to y remap.
        """
        data = {"project_name": project_name, "storage_folder": storage_folder, "z_to_y_remap": z_to_y_remap}
        self.database.upload_data(data, "ApplicationSettings")

    def create_project_data_from_compas(
        self,
        model: Model,
        building_plan: BuildingPlan,
        qr_frames_list: list[Frame],
    ) -> dict:
        """
        Formats data structure from COMPAS Class Objects.

        Parameters
        ----------
        model
            The model from which data will be extracted.
        building_plan
            The BuildingPlan in which data will be extracted from.
        qr_frames_list
            List of frames at specific locations for application localization data.

        """
        qr_model = ModelExtensions().create_qr_model(qr_frames_list)
        if isinstance(model, TimberModel):
            data = {
                "QRFrames": qr_model.__data__,
                "model": model.__data__,
                "beams": {str(beam.guid): beam for beam in model.beams},
                "joints": {str(joint.guid): joint for joint in model.joints},
                "building_plan": building_plan,
            }
        else:
            data = {
                "QRFrames": qr_model.__data__,
                "model": model.__data__,
                "elements": {str(element.guid): element for element in model.elements()},
                "building_plan": building_plan,
            }
        return data

    def upload_data_to_project(self, data: Any, project_name: str, data_name: str) -> None:
        """
        Uploads data to the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        data
            The data to be uploaded.
        project_name
            The name of the project under which the data will be stored.
        data_name
            The name of the child in which data will be stored.
        """
        path = "{}/{}".format(project_name, data_name)
        self.database.upload_data(data, path)

    def upload_project_data_from_compas(
        self,
        project_name: str,
        model: Model,
        building_plan: BuildingPlan,
        qr_frames_list: list[Frame],
    ) -> None:
        """
        Formats data structure from COMPAS Class Objects and uploads them to the RealtimeDatabase under project name.

        Parameters
        ----------
        project_name
            The name of the project under which the data will be stored.
        model
            The model from which data will be extracted.
        building_plan
            The BuildingPlan in which data will be extracted from.
        qr_frames_list
            List of frames at specific locations for application localization data.
        """
        data = self.create_project_data_from_compas(model, building_plan, qr_frames_list)
        self.database.upload_data(data, project_name)

    def upload_qr_frames_to_project(self, project_name: str, qr_frames_list: list[Frame]) -> None:
        """
        Uploads QR Frames to the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        project_name : str
            The name of the project under which the data will be stored.
        qr_frames_list : list[Frame]
            List of frames at specific locations for application localization data.
        """
        qr_model = ModelExtensions().create_qr_model(qr_frames_list)
        data = qr_model.__data__
        path = "{}/{}".format(project_name, "QRFrames")
        self.database.upload_data(data, path)

    def upload_obj_to_storage(self, path_local: str, storage_folder_name: str) -> None:
        """
        Upload an .obj file to the Firebase Storage under the specified storage folder name.

        Parameters
        ----------
        path_local
            The path at which the obj file is stored.
        storage_folder_name
            The name of the storage folder where the .obj file will be uploaded.
        """
        file_name = os.path.basename(path_local)
        storage_path = "obj_storage/{}/{}".format(storage_folder_name, file_name)
        self.storage.upload_file_as_bytes_to_path(path_local, storage_path)

    def upload_objs_from_directory_to_storage(self, local_directory: str, storage_folder_name: str) -> None:
        """
        Uploads all .obj files from a directory to the Firebase Storage under the specified storage folder name.

        Parameters
        ----------
        local_directory
            The path to the directory where the projects .obj files are stored.
        storage_folder_name
            The name of the storage folder where the .obj files will be uploaded.
        """
        if not os.path.exists(local_directory) or not os.path.isdir(local_directory):
            raise FileNotFoundError("Directory not found: {}".format(local_directory))

        for file_name in os.listdir(local_directory):
            local_path = os.path.join(local_directory, file_name)
            if os.path.isfile(local_path):
                storage_path = "obj_storage/{}/{}".format(storage_folder_name, file_name)
                self.storage.upload_file_as_bytes_to_path(local_path, storage_path)

    def get_project_data(self, project_name: str) -> dict:
        """
        Retrieves data from the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        project_name
            The name of the project under which the data will be stored.

        Returns
        -------
        dict
            The data retrieved from the database at the point of fetching.
        """
        return self.database.get_data(project_name)

    def upload_compas_object_to_storage(self, compas_object: Any, cloud_file_name: str, pretty: bool = True) -> None:
        """
        Uploads a COMPAS object to Firebase Storage.

        Parameters
        ----------
        compas_object
            Any compas class instance that is serializable.
        cloud_file_name
            The name of the cloud file. Saved in JSON format, and needs to have a .json extension.

        """
        self.storage.upload_data(compas_object, cloud_file_name, pretty=pretty)

    def get_model_from_storage(self, cloud_file_name: str) -> Model:
        """
        Retrieve a model from Firebase Storage.

        Parameters
        ----------
        cloud_file_name
            The name of the cloud file.

        Returns
        -------
        Model
            The model retrieved from storage.

        """
        return self.storage.get_data(cloud_file_name)

    def edit_step_on_database(
        self,
        project_name: str,
        key: str,
        actor: str,
        is_built: bool,
        is_planned: bool,
        priority: int,
    ) -> None:
        """
        Edits a building plan step in the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        project_name
            The name of the project under which the data will be stored.
        key
            The key of the building plan step to be edited.
        actor
            The actor who will be performing the step.
        is_built
            A boolean that determines if the step is built.
        is_planned
            A boolean that determines if the step is planned.
        priority
            The priority of the step.

        """
        database_path = "{}/building_plan/data/steps/{}/data".format(project_name, key)
        current_data = self.database.get_data(database_path)
        current_data["actor"] = actor
        current_data["is_built"] = is_built
        current_data["is_planned"] = is_planned
        current_data["priority"] = priority
        self.database.upload_data(current_data, database_path)

    def visualize_timber_model_state(
        self,
        timber_model: TimberModel,
        project_name: str,
    ) -> (int, list[Frame], list[Box], list[Box], list[Box], list[Box]):
        """
        Retrieves and visualizes data from the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        timber_model
            The timber model on which the project is based.
        project_name
            The name of the project under which the data will be stored.

        Returns
        -------
        last_built_index : int
            The index of the last built part in the project.
        step_locations : list[Frame]
            The locations of the building plan steps.
        built_human : list[Box]
            The parts that have been built by a human.
        unbuilt_human : list[Box]
            The parts that have not been built by a human.
        built_robot : list[Box]
            The parts that have been built by a robot.
        unbuilt_robot : list[Box]
            The parts that have not been built by a robot.

        """
        building_plan_data_path = "{}/building_plan/data".format(project_name)
        current_state_data = self.database.get_data(building_plan_data_path)

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
        if "PriorityTreeDictionary" in current_state_data:
            current_state_data.pop("PriorityTreeDictionary")

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
            element_id = str(step.element_ids[0])
            element = timber_model.get_element(element_id)
            if element is None:
                raise KeyError("Element {} is not in the timber model.".format(element_id))
            if step.actor == "HUMAN":
                if step.is_built:
                    built_human.append(element.blank)
                else:
                    unbuilt_human.append(element.blank)
            else:
                if step.is_built:
                    built_robot.append(element.blank)
                else:
                    unbuilt_robot.append(element.blank)
        return last_built_index, step_locations, built_human, unbuilt_human, built_robot, unbuilt_robot

    def visualize_project_state(self, model: Model, project_name: str):
        """
        Retrieves and visualizes data from the Firebase RealtimeDatabase under the specified project name.

        Parameters
        ----------
        model
            The model on which the project is based.
        project_name : str
            The name of the project under which the data is stored.

        Returns
        -------
        last_built_index : int
            The index of the last built part in the project.
        step_locations : list[Frame]
            The locations of the building plan steps.
        built_human : list[Element]
            The elements that have been built by a human.
        unbuilt_human : list[Element]
            The elements that have not been built by a human.
        built_robot : list[Element]
            The elements that have been built by a robot.
        unbuilt_robot : list[Element]
            The elements that have not been built by a robot.

        """
        building_plan_data_path = "{}/building_plan/data".format(project_name)
        current_state_data = self.database.get_data(building_plan_data_path)
        elements = {str(element.guid): element for element in model.elements()}

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
            element_id = str(step.element_ids[0])
            try:
                element = elements[element_id]
            except KeyError:
                raise KeyError("Element {} is not in the model.".format(element_id))

            if step.actor == "HUMAN":
                if step.is_built:
                    built_human.append(element)
                else:
                    unbuilt_human.append(element)
            elif step.actor == "ROBOT":
                if step.is_built:
                    built_robot.append(element)
                else:
                    unbuilt_robot.append(element)
            else:
                raise ValueError("Element actor is unknown.")
        return last_built_index, step_locations, built_human, unbuilt_human, built_robot, unbuilt_robot
