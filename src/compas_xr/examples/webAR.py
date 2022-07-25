import os
import compas
from compas.geometry import Scale
from compas.datastructures import Mesh
from compas_xr.datastructures import Scene
from compas_xr.datastructures import Material
from compas_xr.datastructures import PBRMetallicRoughness
from compas_xr import DATA

from compas_xr.examples import upload_to_idl

from paramiko import SSHClient
from paramiko.client import AutoAddPolicy
from scp import SCPClient

import qrcode
import matplotlib.pyplot as plt
import numpy as np


# 1. create GLTF
gltf_filepath = os.path.join(DATA, "mesh_with_material.gltf")
bin_filepath = gltf_filepath.replace(".gltf", ".bin")
webAR_template = os.path.join(DATA, "webAR_template.html")

htmlpage = "webAR_000.html"

color = (1.0, 0.4, 0)
color = (1.0, 1.0, 1.0)
material = Material()
material.name = "Plaster"
material.double_sided = True
material.pbr_metallic_roughness = PBRMetallicRoughness()
material.pbr_metallic_roughness.base_color_factor = list(color) + [1.0]
material.pbr_metallic_roughness.metallic_factor = 0.0
material.pbr_metallic_roughness.roughness_factor = 0.5

scene = Scene()
world = scene.add_layer("world")
mkey = scene.add_material(material)


cmesh = Mesh.from_polyhedron(8)
cmesh = Mesh.from_obj(compas.get("hypar.obj"))

S = Scale.from_factors([0.1, 0.1, 0.1])
cmesh.transform(S)
"""

cmesh = Mesh.from_obj(compas.get("hypar.obj"))
"""

scene.add_layer("element", parent=world, element=cmesh, material=mkey)
scene.to_gltf(gltf_filepath, embed_data=False)


# 2. upload to server

upload_to_idl(gltf_filepath)

"""

scp_username = "w3idl"
scp_password = "WaWrusbawnOiz0"
scp_server = "parterre.ethz.ch"
scr_port = 922
HERE = os.path.dirname(__file__)

upload_directory = "htdocs/webxr"
media_upload = upload_directory + "/media/gltf"


with SSHClient() as ssh:
    ssh.set_missing_host_key_policy(AutoAddPolicy)
    ssh.connect(scp_server, port=scr_port, username=scp_username, password=scp_password)

    scp = SCPClient(ssh.get_transport())

    ftp = ssh.open_sftp()
    files = ftp.listdir(upload_directory)

    #count = 0
    #htmlpage = "webAR_%03d.html" % count
    #while htmlpage in files:
    #    count += 1
    #    htmlpage = "webAR_%03d.html" % count
    #print(htmlpage)

    print("hhere")

    # create from template
    with open(webAR_template, "r") as f:
        html = "".join(f.readlines())
    html = html.replace(
        "{GLTF}", "%s/%s" % ("./media/gltf", os.path.basename(gltf_filepath))
    )
    with open(os.path.join(DATA, htmlpage), "w") as f:
        f.write(html)

    scp.put(os.path.join(DATA, htmlpage), remote_path=upload_directory)
    scp.put(gltf_filepath, remote_path=media_upload)
    scp.put(bin_filepath, remote_path=media_upload)
"""

# 3. show QR code

data = "https://idl.ethz.ch/webxr/%s" % htmlpage
img = qrcode.make(data)
plt.imshow(np.asarray(img), cmap="gray")
plt.show()
