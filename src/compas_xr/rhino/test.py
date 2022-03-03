from compas_xr.rhino.gltf_material import AddMaterial
from compas_rhino import unload_modules
import sys
import scriptcontext

path = r"C:\Users\rustr\workspace\compas_xr\src"
sys.path.append(path)
unload_modules("compas_xr")


print(scriptcontext.doc)
material_index = 642
mat = scriptcontext.doc.Materials[material_index]
print(mat)
M = AddMaterial(mat)
print(M.to_data(1))
