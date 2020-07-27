from ledfx.color import COLORS
from ledfx.color import GRADIENTS
from ledfx.effects.modulatedemo import ModulateEffect
from ledfx.effects.temporal import TemporalEffect
import voluptuous as vol
import numpy as np

class SingleColorEffect(TemporalEffect, ModulateEffect):

    NAME = "Demo"
    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('color', description='Color of strip', default="blue"): vol.In(list(COLORS.keys())),
        vol.Optional('gradient_name', description='Color gradient to display', default = 'Spectral'): vol.In(list(GRADIENTS.keys()))
    })

    def config_updated(self, config):
        self.color = np.array(COLORS[self._config['color']], dtype=float)

    def effect_loop(self):
        color_array = np.tile(self.color, (self.pixel_count, 1))
        self.pixels = self.modulate(color_array)