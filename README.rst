============================================================
compas_xr: COMPAS XR
============================================================

.. start-badges

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://github.com/gramaziokohler/compas_xr/blob/master/LICENSE
    :alt: License MIT

.. image:: https://travis-ci.org/gramaziokohler/compas_xr.svg?branch=master
    :target: https://travis-ci.org/gramaziokohler/compas_xr
    :alt: Travis CI

.. end-badges

.. Write project description

COMPAS XR facilitates XR workflows to foster the application of XR technologies both in research and teaching. It provides interfaces to existing state-of-the-art libraries and software platforms in the XR field (such as NVIDIA Omniverse™), and makes them accessible from within the parametric CAD environment. Compas XR tackles two main problems data conversion (e.g USD, GLB support) and interaction. The package builds upon COMPAS, an open-source Python-based framework for collaboration and research in architecture, engineering and digital fabrication.


Main features
-------------

* feature
* feature
* more features

**compas_xr** runs on Python x.x and x.x.


Documentation
-------------

.. Explain how to access documentation: API, examples, etc.

..
.. optional sections:

Requirements
------------

.. Write requirements instructions here


Installation
------------

Tell Kit to use your python instead: https://docs.omniverse.nvidia.com/py/kit/docs/guide/faq.html

Find :code:`kit-core.json` file. For example:

::

    C:\Users\3duser\AppData\Local\ov\pkg\create 2020.3.2\_build\kit_release\_build\windows-x86_64\release\config\kit-core.json


It has the :code:`/plugins/carb.scripting-python.plugin/pythonHome` key set to use its embedded python.
Change it to your python installation, for instance:

::

    "pythonHome": "C:/Users/3duser/.conda/envs/xr"




.. Write installation instructions here


Contributing
------------

Make sure you setup your local development environment correctly:

* Clone the `compas_xr <https://github.com/gramaziokohler/compas_xr>`_ repository.
* Install development dependencies and make the project accessible from Rhino:

::

    pip install -r requirements-dev.txt
    invoke add-to-rhino

**You're ready to start working!**

During development, use tasks on the
command line to ease recurring operations:

* ``invoke clean``: Clean all generated artifacts.
* ``invoke check``: Run various code and documentation style checks.
* ``invoke docs``: Generate documentation.
* ``invoke test``: Run all tests and checks in one swift command.
* ``invoke add-to-rhino``: Make the project accessible from Rhino.
* ``invoke``: Show available tasks.

For more details, check the `Contributor's Guide <CONTRIBUTING.rst>`_.


Releasing this project
----------------------

.. Write releasing instructions here


.. end of optional sections
..

Credits
-------------

This package was created by Romana Rust <rust@arch.ethz.ch> `@romanarust <https://github.com/romanarust>`_ at `@gramaziokohler <https://github.com/gramaziokohler>`_
