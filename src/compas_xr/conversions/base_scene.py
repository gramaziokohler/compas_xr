class BaseScene(object):
    """Base Scene class for conversions"""

    def __init__(self, name="BaseScene"):
        from compas_xr.datastructures import Scene

        self.name = name
        self.scene = Scene(name=self.name)

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
        return self.scene
