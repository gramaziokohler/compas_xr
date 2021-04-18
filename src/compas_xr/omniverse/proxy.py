import sys
sys.path.append(r"C:\Users\3duser\.conda\envs\xr\Lib\site-packages")
sys.path.append(r"C:\Users\3duser\workspace\compas_xr\src")

from compas.rpc.services.default import start_service

def start(port, autoreload, **kwargs):
    start_service(port, autoreload)

if __name__ == '__main__':
    start(port=1753, autoreload=True)

# kit.exe  --enable omni.client --exec proxy.py
