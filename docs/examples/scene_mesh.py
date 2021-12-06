import os
from compas.datastructures import Mesh
from compas_xr import DATA
from compas_xr.datastructures import Scene

scene = Scene()

mesh = Mesh.from_polyhedron(8)
world = scene.add_layer("world")
poly = scene.add_layer("poly", element=mesh, parent="world")

scene.to_gltf(os.path.join(DATA, "poly.gltf"))
scene.to_usd(os.path.join(DATA, "poly.usda"))
