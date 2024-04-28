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


__author__ = ["Joseph Kenny"]
__copyright__ = "Gramazio Kohler Research"
__license__ = "MIT License"
__email__ = "kenny@arch.ethz.ch"
__version__ = "0.1.0"


HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "data"))

__all_plugins__ = ["compas_xr.rhino.install"]
__all__ = ["HERE", "DATA"]