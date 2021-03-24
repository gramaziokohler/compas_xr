from compas.geometry import Frame
from compas.geometry import Transformation

def worldYup2worldZup(frame):
    """
    """
    F = Frame((0, 0, 0), (1, 0, 0), (0, 0, -1))
    T = Frame((0, 0, 0), (1, 0, 0), (0, 1, 0))
    return frame.transformed(Transformation.from_frame_to_frame(F, T))


if __name__ == "__main__":
    print(worldYup2worldZup(Frame.worldXY()))