from .material import *  # noqa F403
from .scene import GLTFScene  # noqa F403

"""
from enum import Enum
class AlphaMode(Enum):
    BLEND = 'BLEND'
    MASK = 'MASK'
    OPAQUE = 'OPAQUE'
"""


class AlphaMode(object):  # todo upstream!
    BLEND = "BLEND"
    MASK = "MASK"
    OPAQUE = "OPAQUE"
