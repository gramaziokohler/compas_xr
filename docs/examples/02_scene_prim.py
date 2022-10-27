import os
from compas.geometry import Box
from compas.geometry import Cylinder, Circle, Plane
from compas.geometry import Frame

from compas_xr import DATA
from compas_xr.datastructures import Scene

scene = Scene()
world = scene.add_layer("world")

box = Box(Frame.worldXY(), 1.0, 1.0, 1.0)
box_key = scene.add_layer("box", element=box, frame=Frame((1, 0, 0), (1, 0, 0), (0, 1, 0)), parent="world")

cy = Cylinder(Circle(Plane([0, 0, 0], [0, 0, 1]), 0.5), 2)
cy_key = scene.add_layer("cy", element=cy, frame=Frame((2, 0, 0), (1, 0, 0), (0, 1, 0)), parent="world")

scene.to_gltf(os.path.join(DATA, "scene_prim.gltf"))
scene.to_usd(os.path.join(DATA, "scene_prim.usda"))
