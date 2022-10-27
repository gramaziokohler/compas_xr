"""Execute this file with kit

kit.exe --empty --enable omni.client --enable omni.usd --exec omniverse_connect.py
"""
import asyncio

from compas.geometry import Frame
from compas.geometry import Box
from compas_xr.omniverse import open_stage_live
from compas_xr.omniverse import save_stage
from compas_xr.usd import prim_from_box

URL = "omniverse://localhost/Users/rustr/compas_xr/test_scene.usda"


async def main():
    # open scene live
    stage = await open_stage_live(URL)
    box = Box(Frame.worldXY(), 1.0, 1.0, 1.0)
    prim = prim_from_box(stage, "/World/box", box)
    print(prim)
    await save_stage(stage)


if __name__ == "__main__":
    asyncio.run(main())
