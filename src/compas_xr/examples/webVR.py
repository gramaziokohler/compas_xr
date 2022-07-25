from compas_xr.examples import upload_to_idl_vr

gltf_filepath = (
    r"C:\Users\rustr\workspace\compas_xr\src\compas_xr\data\mesh_with_material.gltf"
)
upload_to_idl_vr(gltf_filepath, htmlpage="webVR_001.html")
