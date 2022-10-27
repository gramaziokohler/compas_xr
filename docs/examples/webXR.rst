*******************************************************************************
Working with WebXR
*******************************************************************************

If you want to create a scene and use your Augmented Reality (AR) or Virtual
Reality (VR) device to quickly view it you can also use
`webXR <https://immersiveweb.dev/>`_.

AR Example
==========

First we create a scene.

.. code-block:: python

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


Then we use the webAR template to create a webpage.

.. code-block:: python

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


We start a local server on port 8000.

::

    python -m http.server


We copy necessary files from https://immersive-web.github.io/webxr-samples.

We generate a QR code to scan with the phone.

.. code-block:: python

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


VR Example
==========

We use the scene from above.

We use the webVR template to create a webpage.

.. code-block:: python

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

Then we simply use a broser to navigate to the webpage `http://127.0.0.1:8000/webVR.html <http://127.0.0.1:8000/webVR.html>`_.

`Link to full script <webXR/AR_and_VR.py>`_