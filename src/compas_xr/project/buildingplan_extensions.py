from compas_model.models import Model
from compas_timber.planning import BuildingPlan
from compas_timber.planning import SimpleSequenceGenerator
from compas_timber.planning import Step


class BuildingPlanExtensions:
    """
    Extensions for the [BuildingPlan][] class.

    This class provides functionality to create a building plan from an established model sequence.
    """

    # TODO: This makes the building plan in a very manual way
    # TODO: but this needs to be resolved in tandem with building plan revisions.
    def create_buildingplan_from_model_sequence(
        self,
        model: Model,
        data_type: int,
        robot_keys: list[str] = None,
        priority_keys_lists: list[list[str]] = None,
    ) -> BuildingPlan:
        """
        Create a [BuildingPlan][] based on the sequence of the model elements.

        Parameters
        ----------
        model
            The model for which to generate the building plan.
        data_type
            List index of which data type will be loaded on the application side [0: 'Cylinder', 1: 'Box', 2: 'ObjFile']
        robot_keys
            List of keys that are intended to be built by the robot.
        priority_keys_lists
            Lists of element GUIDs that can be built in parallel, in model order.

        Returns
        -------
        [BuildingPlan][]
            The building plan generated from the model sequence.

        """
        data_type_list = ["0.Cylinder", "1.Box", "2.ObjFile"]
        building_plan = SimpleSequenceGenerator(model=model).result

        for step in building_plan.steps:
            step.geometry = data_type_list[data_type]
            # TODO: These are unused for now, but are expeted on the application side
            step.instructions = ["none"]
            step.elements_held = [0]

            element_key = str(step.element_ids[0])
            if robot_keys:
                if element_key in robot_keys:
                    step.actor = "ROBOT"

            if not priority_keys_lists:
                step.priority = 0
            else:
                for i, keys_list in enumerate(priority_keys_lists):
                    if element_key in keys_list:
                        step.priority = i
                        break

        return building_plan

    def create_buildingplan_from_custom_sequence(
        self,
        model: Model,
        sequenced_keys: list[str],
        data_type: int,
        robot_keys: list[str],
        priority_keys_lists: list[list[str]],
    ) -> BuildingPlan:
        """
        Create a [BuildingPlan][] based on a custom sequence of model elements.

        Parameters
        ----------
        model
            The model for which to generate the building plan.
        sequenced_keys
            List of element GUIDs in the intended build order.
        data_type
            List index of which data type will be loaded on the application side [0: 'Cylinder', 1: 'Box', 2: 'ObjFile']
        robot_keys
            List of keys that are intended to be built by the robot.
        priority_keys_lists
            Lists of element GUIDs that can be built in parallel, in model order.

        Returns
        -------
        [BuildingPlan][]
            The building plan generated from the custom model sequence.

        """
        data_type_list = ["0.Cylinder", "1.Box", "2.ObjFile"]
        elements = {str(element.guid): element for element in model.elements()}
        building_plan = BuildingPlan()

        for key in sequenced_keys:
            try:
                element = elements[str(key)]
            except KeyError:
                raise KeyError("Element {} is not in the model.".format(key))

            step = Step([str(key)])
            step.geometry = data_type_list[data_type]
            # TODO: These are unused for now, but are expeted on the application side
            step.instructions = ["none"]
            step.elements_held = [0]
            step.location = element.frame

            if robot_keys:
                if key in robot_keys:
                    step.actor = "ROBOT"
                else:
                    step.actor = "HUMAN"
            else:
                step.actor = "HUMAN"

            if not priority_keys_lists:
                step.priority = 0
            else:
                for i, keys_list in enumerate(priority_keys_lists):
                    if key in keys_list:
                        step.priority = i
                        break
            building_plan.add_step(step)

        return building_plan
