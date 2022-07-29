from .material import *  # noqa F403
from .scene import GLTFScene  # noqa F403


class AlphaMode(object):  # todo upstream!
    BLEND = "BLEND"
    MASK = "MASK"
    OPAQUE = "OPAQUE"
