"""
********************************************************************************
compas_xr.storage
********************************************************************************

This package contains classes for data storage using Firebase.

.. currentmodule:: compas_xr.storage

Classes
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Storage

"""

import sys

if sys.platform == "cli":
    from compas_xr.storage.storage_cli import Storage
else:
    from compas_xr.storage.storage_pyrebase import Storage

__all__ = ["Storage"]
