import os
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy
from scp import SCPClient
from compas_xr import DATA

scp_username = "w3idl"
scp_password = "WaWrusbawnOiz0"
scp_server = "parterre.ethz.ch"
scr_port = 922
HERE = os.path.dirname(__file__)

upload_directory = "htdocs/webxr"
media_upload = upload_directory + "/media/gltf"

webAR_template = os.path.join(DATA, "webAR_template.html")


def upload_to_idl(gltf_filepath, htmlpage="webAR_000.html"):

    bin_filepath = gltf_filepath.replace(".gltf", ".bin")

    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy)
        ssh.connect(
            scp_server, port=scr_port, username=scp_username, password=scp_password
        )
        print(ssh.get_transport().active)
        scp = SCPClient(ssh.get_transport())

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


def upload_to_idl_vr(
    gltf_filepath, htmlpage="webVR_000.html", template="webVR_template.html"
):

    webVR_template = os.path.join(DATA, "webVR_template.html")

    bin_filepath = gltf_filepath.replace(".gltf", ".bin")

    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy)
        ssh.connect(
            scp_server, port=scr_port, username=scp_username, password=scp_password
        )
        print(ssh.get_transport().active)
        scp = SCPClient(ssh.get_transport())

        # create from template
        with open(webVR_template, "r") as f:
            html = "".join(f.readlines())
        html = html.replace(
            "{GLTF}", "%s/%s" % ("./media/gltf", os.path.basename(gltf_filepath))
        )
        with open(os.path.join(DATA, htmlpage), "w") as f:
            f.write(html)

        scp.put(os.path.join(DATA, htmlpage), remote_path=upload_directory)
        scp.put(gltf_filepath, remote_path=media_upload)
        scp.put(bin_filepath, remote_path=media_upload)
        print(media_upload)
        print(gltf_filepath)
        print(bin_filepath)
        print(upload_directory, htmlpage)
