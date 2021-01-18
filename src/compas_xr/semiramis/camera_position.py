import math
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import Frame


def camera_position(target, angle, radius, z):
    """
    """
    target = Point(*list(target))
    xaxis = Vector(1, 0, 0)
    yaxis = Vector(0, 1, 0)
    zaxis = Vector(0, 0, 1)

    x = math.cos(angle) * radius
    y = math.sin(angle) * radius

    location = target + xaxis * x + yaxis * y
    location.z = z

    direction = location - target
    camera_up = zaxis

    xaxis = camera_up.cross(direction)
    yaxis = direction.cross(xaxis)
    return Frame(location, xaxis, yaxis)
