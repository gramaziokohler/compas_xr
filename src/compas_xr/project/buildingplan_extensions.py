from compas_timber.planning import SimpleSequenceGenerator


class BuildingPlanExtensions(object):
    """
    BuildingPlanExtensions is a class for extending the functionality of the compas_timber.planning.BuildingPlan class.

    The BuildingPlanExtensions class provides additional functionalities to the compas_timber.planning.BuildingPlan class
    by providing a way to create a buildling plan from an established assembly sequence.

    Parameters
    ----------
    param1 : type
        Description of param1.

    Attributes
    ----------
    None
    """

    # TODO: This makes the building plan in a very manual way, but this needs to be resolved in tandem with building plan revisions.
    def create_buildingplan_from_assembly_sequence(self, assembly, data_type, robot_keys, priority_keys_lists):
        """
        Create a compas_timber.planning.BuildingPlan based on the sequence of the assembly parts.

        Parameters
        ----------
        assembly : compas_timber.assembly.TimberAssembly or compas.datastructures.Assembly
            The assembly that you want to generate the buiding plan for.
        data_type : int
            List index of which data type will be loaded on the application side [0: 'Cylinder', 1: 'Box', 2: 'ObjFile']
        robot_keys : list of str
            List of keys that are intended to be built by the robot.
        priority_keys_lists : list of list of str
            List in assembly order of lists of assembly keys that can be built in parallel.

        Returns
        -------
        None

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
