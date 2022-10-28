import os
import math
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry.transformations.rotation import Rotation
from compas.geometry.transformations.translation import Translation

from compas_xr import DATA
from compas_xr.datastructures import Scene

scene = Scene()
world = scene.add_layer("world")
world = scene.add_layer("references")

box = Box(Frame.worldXY(), 1.0, 1.0, 1.0)
# better: scene.add_reference("box", element=box), auto create references layer, auto is_reference=True
box_key = scene.add_layer("box", element=box, is_reference=True, parent="references")

for i, angle in enumerate(range(0, 360, 60)):
    T = Translation.from_vector((2, 0, 0))
    R = Rotation.from_axis_and_angle((0, 0, 1), math.radians(angle))
    frame = Frame.from_transformation(R * T)
    # better: scene.add_element_to_layer()
    scene.add_layer("box%d" % i, instance_of=box_key, frame=frame, parent="world")

scene.to_gltf(os.path.join(DATA, "scene_instances.gltf"))
scene.to_usd(os.path.join(DATA, "scene_instances.usda"))
