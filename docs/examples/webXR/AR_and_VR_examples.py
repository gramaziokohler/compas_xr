import os
import compas
from compas.geometry import Scale
from compas.datastructures import Mesh
from compas_xr.datastructures import Scene
from compas_xr.datastructures import Material
from compas_xr.datastructures import PBRMetallicRoughness

HERE = os.path.dirname(__file__)


gltf_filepath = os.path.join(HERE, "mesh_with_material.gltf")


def create_scene():

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

    cmesh = Mesh.from_obj(compas.get("hypar.obj"))
    S = Scale.from_factors([0.1, 0.1, 0.1])
    cmesh.transform(S)
    scene.add_layer("element", parent=world, element=cmesh, material=mkey)

    scene.to_gltf(gltf_filepath, embed_data=False)


def create_AR_page():
    webAR_template = os.path.join(HERE, "webAR_template.html")
    webAR_filepath = os.path.join(HERE, "webAR.html")

    # read
    with open(webAR_template, "r") as f:
        html = "".join(f.readlines())
    # replace
    html = html.replace("{GLTF}", os.path.basename(gltf_filepath))
    # write
    with open(os.path.join(HERE, webAR_filepath), "w") as f:
        f.write(html)


def show_qr_code():

    import qrcode
    import matplotlib.pyplot as plt
    import numpy as np
    import socket

    hostname = socket.getfqdn()
    port = 8000
    htmlpage = "http://%s:%i/%s" % (hostname, port, "webAR.html")

    img = qrcode.make(htmlpage)
    plt.imshow(np.asarray(img), cmap="gray")
    plt.show()


def create_VR_page():
    webVR_template = os.path.join(HERE, "webVR_template.html")
    webVR_filepath = os.path.join(HERE, "webVR.html")

    # read
    with open(webVR_template, "r") as f:
        html = "".join(f.readlines())
    # replace
    html = html.replace("{GLTF}", os.path.basename(gltf_filepath))
    # write
    with open(os.path.join(HERE, webVR_filepath), "w") as f:
        f.write(html)


if __name__ == "__main__":
    create_scene()
    create_AR_page()
    create_VR_page()
    show_qr_code()
