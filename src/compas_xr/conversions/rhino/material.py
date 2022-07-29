import Rhino
import scriptcontext

from compas_xr.conversions import BaseMaterial


class RhinoMaterial(BaseMaterial):
    """RhinoMaterial"""

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

    @classmethod
    def get_object_material(cls, obj):
        source = obj.Attributes.MaterialSource
        if source == Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject:
            return obj.RenderMaterial
        elif source == Rhino.DocObjects.ObjectMaterialSource.MaterialFromLayer:
            layer_index = obj.Attributes.LayerIndex
            return cls.get_layer_material(layer_index)
        else:
            return None

    @classmethod
    def get_layer_material(cls, layer_index):
        if layer_index < 0 or layer_index >= scriptcontext.doc.Layers.Count:
            return None
        else:
            return scriptcontext.doc.Layers[layer_index].RenderMaterial
