"""

COMPAS XR facilitates XR workflows to foster the application of XR technologies both in research and teaching. 
It provides interfaces to existing state-of-the-art libraries and software platforms in the XR field (such as NVIDIA Omniverse™), 
and makes them accessible from within the parametric CAD environment. 

Compas XR tackles two core problems: data conversion (e.g USD, GLB support) and (-soon to come-) interaction. 
The package builds upon COMPAS, an open-source Python-based framework for collaboration and research in architecture, 
engineering and digital fabrication.


Main concepts
=============

Scene
-----

.. autoclass:: Scene
   :members:


Material
-----

.. autoclass:: Material
   :members:

"""
import os

from .__version__ import __version__
from .datastructures import Scene
from .datastructures import Material

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "data")

__all__ = [
    "__version__",
    "Scene",
    "Material",
]
