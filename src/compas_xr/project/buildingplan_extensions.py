from compas_timber.planning import BuildingPlan
from compas_timber.planning import SimpleSequenceGenerator
from compas_timber.planning import Step


class BuildingPlanExtensions(object):
    """
    BuildingPlanExtensions is a class for extending the functionality of the :class:`~compas_timber.planning.BuildingPlan` class.

    The BuildingPlanExtensions class provides additional functionalities to the :class:`~compas_timber.planning.BuildingPlan`
    by providing a way to create a buildling plan from an established assembly sequence.
    """

    # TODO: This makes the building plan in a very manual way
    # TODO: but this needs to be resolved in tandem with building plan revisions.
    def create_buildingplan_from_assembly_sequence(self, assembly, data_type, robot_keys, priority_keys_lists):
        """
        Create a compas_timber.planning.BuildingPlan based on the sequence of the assembly parts.

        Parameters
        ----------
        assembly : :class:`~compas_timber.assembly.TimberAssembly` or :class:`~compas.datastructures.Assembly`
            The assembly that you want to generate the buiding plan for.
        data_type : int
            List index of which data type will be loaded on the application side [0: 'Cylinder', 1: 'Box', 2: 'ObjFile']
        robot_keys : list of str
            List of keys that are intended to be built by the robot.
        priority_keys_lists : list of list of str
            List in assembly order of lists of assembly keys that can be built in parallel.

        Returns
        -------
        building_plan : :class:`~compas_timber.planning.BuildingPlan`
            The building plan generated from the assembly sequence.

        """
        data_type_list = ["0.Cylinder", "1.Box", "2.ObjFile"]
        building_plan = SimpleSequenceGenerator(assembly=assembly).result

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
    
    def create_buildingplan_from_with_custom_sequence(self, assembly, sequenced_keys, data_type, robot_keys, priority_keys_lists):
        """
        Create a compas_timber.planning.BuildingPlan based on the sequence of the assembly parts.

        Parameters
        ----------
        assembly : compas_timber.assembly.TimberAssembly or compas.datastructures.Assembly
            The assembly that you want to generate the buiding plan for.
        sequenced_keys : list of str
            List of keys that are intended to be built in the order provided.
        data_type : int
            List index of which data type will be loaded on the application side [0: 'Cylinder', 1: 'Box', 2: 'ObjFile']
        robot_keys : list of str
            List of keys that are intended to be built by the robot.
        priority_keys_lists : list of list of str
            List in assembly order of lists of assembly keys that can be built in parallel.

        Returns
        -------
        building_plan : compas_timber.planning.BuildingPlan
            The building plan generated from the assembly sequence.

        """
        data_type_list = ["0.Cylinder", "1.Box", "2.ObjFile"]
        graph_data = assembly.graph.__data__
        node_data = graph_data['node']
        building_plan = BuildingPlan()

        for key in sequenced_keys:
            step = Step(key)
            # TODO: This is dumb, but the element_ids are generated incorrectly so they are overwritten here
            step.element_ids = [key]            
            step.geometry = data_type_list[data_type]
            # TODO: These are unused for now, but are expeted on the application side
            step.instructions = ["none"]
            step.elements_held = [0]
            step.location = node_data[str(key)]["part"].frame

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
