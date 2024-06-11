"""
********************************************************************************
compas_xr.realtime_database
********************************************************************************

This package contains classes for using Firebase realtime database.

.. currentmodule:: compas_xr.realtime_database

Classes
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    RealtimeDatabase

"""

import sys

if sys.platform == "cli":
    from compas_xr.realtime_database.realtime_database_cli import RealtimeDatabase
else:
    from compas_xr.realtime_database.realtime_database_pyrebase import RealtimeDatabase

__all__ = ["RealtimeDatabase"]
