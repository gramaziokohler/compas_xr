"""
********************************************************************************
compas_xr
********************************************************************************

.. currentmodule:: compas_xr


.. toctree::
    :maxdepth: 1


"""

from __future__ import print_function

import os
# from .realtime_database import RealtimeDatabase
# from .storage import Storage


__author__ = ["GKR"]
__copyright__ = "Gramazio Kohler Research"
__license__ = "MIT License"
__email__ = "mitterberger@arch.ethz.ch"
__version__ = "0.1.0"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))
SCRIPT = os.path.abspath(os.path.join(HOME, "scripts"))

# def storage_instance(default_file_path, config_path):

#     storage = Storage(default_file_path, config_path)

#     return storage

# def realtime_database_instance(default_file_path, config_path):

#     realtime_database = RealtimeDatabase(default_file_path, config_path)

#     return realtime_database

# def print_instance():

#     print = Print()

#     return print

__all_plugins__ = ["compas_xr.rhino.install"]
__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
