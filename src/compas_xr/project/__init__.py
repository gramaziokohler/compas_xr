"""
********************************************************************************
compas_xr.project
********************************************************************************

This package contains classes to manage the XR project including the assembly
and building plan.

.. currentmodule:: compas_xr.project

Classes
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    ProjectManager
    AssemblyExtensions
    BuildingPlanExtensions

"""

from compas_xr.project.assembly_extensions import AssemblyExtensions
from compas_xr.project.buildingplan_extensions import BuildingPlanExtensions
from compas_xr.project.project_manager import ProjectManager

__all__ = ["ProjectManager", "AssemblyExtensions", "BuildingPlanExtensions"]
