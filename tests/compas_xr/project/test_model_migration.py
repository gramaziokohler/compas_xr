from importlib.metadata import version

from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Vector
from compas_model.elements import BeamElement
from compas_model.models import Model
from compas_pb import pb_dump_bts
from compas_pb import pb_load_bts

from compas_xr.project import BuildingPlanExtensions
from compas_xr.project import ModelExtensions
from compas_xr.project import ProjectManager


def test_compas_pb_1_1_is_installed():
    assert version("compas_pb").startswith("1.1.")


def test_qr_model_roundtrips_with_compas_pb():
    frames = [
        Frame.worldXY(),
        Frame(Point(1, 2, 3), Vector.Xaxis(), Vector.Yaxis()),
    ]

    model = ModelExtensions().create_qr_model(frames)
    restored = pb_load_bts(pb_dump_bts(model))

    assert isinstance(restored, Model)
    assert [element.name for element in restored.elements()] == ["QR_0", "QR_1"]
    assert [element.frame for element in restored.elements()] == frames


def test_building_plan_uses_model_element_guids():
    model = ModelExtensions().create_qr_model([Frame.worldXY(), Frame.worldYZ()])
    elements = list(model.elements())

    plan = BuildingPlanExtensions().create_buildingplan_from_model_sequence(
        model,
        data_type=2,
        robot_keys=[str(elements[1].guid)],
    )

    assert [step.element_ids for step in plan.steps] == [[str(element.guid)] for element in elements]
    assert [step.actor for step in plan.steps] == [0, 1]
    assert [step.geometry for step in plan.steps] == ["2.ObjFile", "2.ObjFile"]


def test_custom_sequence_uses_requested_model_order():
    model = ModelExtensions().create_qr_model([Frame.worldXY(), Frame.worldYZ()])
    elements = list(model.elements())
    sequence = [str(elements[1].guid), str(elements[0].guid)]

    plan = BuildingPlanExtensions().create_buildingplan_from_custom_sequence(
        model,
        sequenced_keys=sequence,
        data_type=0,
        robot_keys=[],
        priority_keys_lists=[],
    )

    assert [step.element_ids[0] for step in plan.steps] == sequence
    assert [step.location for step in plan.steps] == [elements[1].frame, elements[0].frame]


def test_mesh_model_obj_export_uses_element_guid(tmp_path):
    model = Model()
    element = model.add_element(BeamElement())

    ModelExtensions().export_mesh_model_objs(model, str(tmp_path), "obj")

    assert (tmp_path / "obj" / "{}.obj".format(element.guid)).is_file()


def test_project_data_uses_model_and_elements_keys():
    model = ModelExtensions().create_qr_model([Frame.worldXY()])
    plan = BuildingPlanExtensions().create_buildingplan_from_model_sequence(model, data_type=0)
    manager = ProjectManager.__new__(ProjectManager)

    data = manager.create_project_data_from_compas(model, plan, [Frame.worldXY()])

    assert set(data) == {"QRFrames", "model", "elements", "building_plan"}
    assert set(data["elements"]) == {str(element.guid) for element in model.elements()}
