"""Execute this file with kit

kit.exe --empty --enable omni.client --enable omni.usd --exec connect.py
"""
import sys
import asyncio

sys.path.append(r"C:\Users\rustr\workspace\compas\src")
sys.path.append(r"C:\Users\rustr\workspace\compas_xr\src")

import compas
from compas.geometry import Frame
from compas.geometry import Box
from compas_xr.omniverse import open_stage_live
from compas_xr.omniverse import save_stage
from compas_xr.usd import prim_from_sphere

URL = "omniverse://localhost/Users/rustr/test/test.usd"

spheres = compas.json_load(r"C:\Users\rustr\workspace\compas_xr\grasshopper\spheres.json")

async def main():
    # open scene live
    stage = await open_stage_live(URL)

    for i, sphere in enumerate(spheres):
        prim = prim_from_sphere(stage, "/World/sphere%i" % i, sphere)
    await save_stage(stage)
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())