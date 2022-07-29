class BaseMaterial(object):
    """Base Material class for conversions"""

    @classmethod
    def from_material(cls, material):
        """Construct a material.

        Parameters
        ----------
        material : :class:`compas_xr.datastructures.Material`
        """
        raise NotImplementedError

    def to_compas(self):
        """Convert to a COMPAS object.

        Returns
        -------
        :class:`compas_xr.datastructures.Material`
            A COMPAS material.
        """
        raise NotImplementedError
