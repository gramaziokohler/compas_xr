import math

import compas
import numpy
import pytest

import compas_xr


def pytest_ignore_collect(collection_path):
    if "rhino" in str(collection_path):
        return True

    if "blender" in str(collection_path):
        return True

    if "ghpython" in str(collection_path):
        return True


@pytest.fixture(autouse=True)
def add_compas(doctest_namespace):
    doctest_namespace["compas"] = compas


@pytest.fixture(autouse=True)
def add_compas_xr(doctest_namespace):
    doctest_namespace["compas_xr"] = compas_xr


@pytest.fixture(autouse=True)
def add_math(doctest_namespace):
    doctest_namespace["math"] = math


@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    doctest_namespace["np"] = numpy
