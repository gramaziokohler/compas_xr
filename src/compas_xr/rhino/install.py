from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import os

import compas
import compas.plugins
from compas_ghpython.components import install_userobjects
from compas_ghpython.components import uninstall_userobjects


@compas.plugins.plugin(category="install")
def installable_rhino_packages():
    return ["compas_xr"]


@compas.plugins.plugin(category="install")
def after_rhino_install(installed_packages):
    project = "compas_xr"
    if project not in installed_packages:
        return []

    srcdir = os.path.join(os.path.dirname(__file__), "..", "ghpython", "components", "ghuser")
    installed_objects = install_userobjects(srcdir)
    msg = "Installed {} GH User Objects".format(len(installed_objects))

    return [(project, msg, True)]


@compas.plugins.plugin(category="install")
def after_rhino_uninstall(uninstalled_packages):
    project = "compas_xr"
    if project not in uninstalled_packages:
        return []

    srcdir = os.path.join(os.path.dirname(__file__), "..", "ghpython", "components", "ghuser")
    userobjects = [os.path.basename(ghuser) for ghuser in glob.glob(os.path.join(srcdir, "*.ghuser"))]
    uninstalled_objects = uninstall_userobjects(userobjects)

    uninstall_errors = [uo[0] for uo in uninstalled_objects if not uo[1]]
    error_msg = "" if not uninstall_errors else "and {} failed to uninstall".format(len(uninstall_errors))
    msg = "Uninstalled {} GH User Objects {}".format(len(uninstalled_objects), error_msg)

    return [(project, msg, True)]
