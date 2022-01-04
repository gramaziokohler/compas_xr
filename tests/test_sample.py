

def test_calculate_answer():
    assert 42 == 42


if __name__ == "__main__":
    import os
    from compas_xr import DATA
    from pxr import Usd, UsdGeom, Gf, Sdf

    url = os.path.join(DATA, "camera_spin.usda")

    stage = Usd.Stage.Open(url)

    path = "/World/Xform"
    top = stage.GetPrimAtPath(path)
    xform = UsdGeom.Xformable(top)
    spin = xform.AddRotateYOp(opSuffix='spin')
    spin.Set(time=1, value=0)
    spin.Set(time=192, value=360)

    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(192)
    stage.Save()
