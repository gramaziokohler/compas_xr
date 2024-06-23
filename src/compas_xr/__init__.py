"""
********************************************************************************
compas_xr
********************************************************************************

.. currentmodule:: compas_xr


.. toctree::
    :maxdepth: 1

    compas_xr.ghpython
    compas_xr.mqtt
    compas_xr.project
    compas_xr.realtime_database
    compas_xr.storage

"""

from __future__ import print_function

import os


__author__ = ["Joseph Kenny"]
__copyright__ = "ETH Zurich, Princeton University"
__license__ = "MIT License"
__email__ = "kenny@arch.ethz.ch"
__version__ = "0.8.0"


HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "data"))

__all_plugins__ = ["compas_xr.rhino.install"]
__all__ = ["HERE", "DATA"]
