from ledfx.color import COLORS
from ledfx.effects.modulate import ModulateEffect
from ledfx.effects.temporal import TemporalEffect
from ledfx.effects.modulate import ModulateEffect
from PIL import Image
import voluptuous as vol
import numpy as np

class SingleColorEffect(TemporalEffect, ModulateEffect):

    NAME = "Single Color"
    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('color', description='Color of strip', default="red"): vol.In(list(COLORS.keys())),
    })

    def config_updated(self, config):
        self.color = np.array(COLORS[self._config['color']], dtype=float)

    def effect_loop(self):
        self.pixels = Image.new("RGB", (self.pixel_count, 1), color=self.color)
