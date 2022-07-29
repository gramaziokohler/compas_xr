class BaseScene(object):
    """Base Scene class for conversions"""

    @classmethod
    def from_scene(cls, scene):
        """Construct a scene.

        Parameters
        ----------
        scene : :class:`compas_xr.datastructures.Scene`
        """
        raise NotImplementedError

    def to_compas(self):
        """Convert to a COMPAS object.

        Returns
        -------
        :class:`compas_xr.datastructures.Scene`
            A COMPAS scene.
        """
        raise NotImplementedError
