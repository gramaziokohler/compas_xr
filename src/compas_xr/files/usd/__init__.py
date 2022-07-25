import compas

if not compas.IPY:
    from .usd import *  # noqa F403
    from .material import *  # noqa F403
    from .scene import USDScene
