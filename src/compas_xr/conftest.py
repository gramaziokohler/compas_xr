import os
import pytest
from compas_xr.datastructures import Material
from compas_xr.datastructures import PBRMetallicRoughness


@pytest.fixture(autouse=True)
def add_imports(doctest_namespace):
    doctest_namespace["os"] = os
    doctest_namespace["Material"] = Material
    doctest_namespace["PBRMetallicRoughness"] = PBRMetallicRoughness
