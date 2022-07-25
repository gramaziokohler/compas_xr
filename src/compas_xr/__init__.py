"""

Intro to project ...


Setup
=====

In order to use this library, ...


Main concepts
=============

Describe typical classes found in project

.. autoclass:: SampleClassName
   :members:


"""
import os

DATA = os.path.join(os.path.dirname(__file__), "data")

IN_OMNI = False
try:
    import omni  # noqa F401

    IN_OMNI = True
except ModuleNotFoundError:
    IN_OMNI = False
