********************************************************************************
Installation
********************************************************************************

This chapter provides a step-by-step guide for installing compas_xr on your system. The library can be
installed using either pip or conda, which are widely-used package managers for Python. The following
instructions will guide you through each method. Alternatively, you can clone the ``compas_xr`` library
directly from our `repository <https://github.com/gramaziokohler/compas_xr>`_.

Installation using conda
========================

Conda is an open-source package management system and environment management system that runs on Windows,
macOS, and Linux. It is very popular in the realm of scientific computing.

Step 1: Create a conda environment (Optional)
=============================================

It's often beneficial to create a new environment for your project. This can be done using the following command:
::
    conda create --name my_environment_name

Replace my_environment_name with your desired environment name.

Activate the new environment by running:
::
    conda activate my_environment_name

Step 2: Update pip
==================

It is good practice to ensure that you are using the latest version of pip. To update pip, run the following command:
::
    python -m pip install --upgrade pip

Step 3: Install compas_xr
=========================

To install compas_xr using pip, execute the following command:
::
    pip install compas_xr

Verify installation
===================

After installation, you can verify that the compas_xr has been successfully installed by running:
::
    python -c "import compas_xr; print(compas_xr.__version__)"


If everything worked out correctly, the version of the installed package will be printed on the screen, and you can
start using the toolkit into your projects.

Installing COMPAS packages for Rhino environments
=================================================

After verification of installation you can run the command below to install all COMPAS packages within your Rhino Environment:
::
    python -m compas_rhino.install

COMPAS XR Unity - Phone Based AR Application
============================================

This chapter provides a step-by-step guide for installing compas_xr_unity on your device. The use and installation of
the application is supported by both Android and ios devices. If you would like to install the application without
functionality or code modifications Android .apk file, and ios xcode build can be found `here <https://github.com/gramaziokohler>`_.

However, if you would like to modify any application functionalities or anything the entire code base for the application
can be found and cloned from our `repository <https://github.com/gramaziokohler/compas_xr>`_.

Additionally, both Android and device installation procedures can be found in the Release Procedures chapter of the documentation.
