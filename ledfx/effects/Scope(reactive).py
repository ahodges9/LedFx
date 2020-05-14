from ledfx.effects.audio import AudioReactiveEffect
from ledfx.color import COLORS
from PIL import Image, ImageDraw
import voluptuous as vol
import numpy as np


class Strobe(AudioReactiveEffect):
    NAME = "Scope"
    CONFIG_SCHEMA = vol.Schema({
    })

    def config_updated(self, config):
        return

    def audio_data_updated(self, data):
        samples = data.audio_sample(raw=True)
        image = Image.new("RGB", self._dimensions, color=0)
        img1 = ImageDraw.Draw(image)

        dx = len(samples)/self._dimensions[0]
        py = 0
        for x in range(0, self._dimensions[0]):
            v = np.mean(samples[int(x*dx):int((x+1)*dx)])
            y = int(self._dimensions[1]/2+v*self._dimensions[1]/2)
            if x > 0:
                img1.line(((x-1, py), (x, y)), width=1)
            py = y
        self.image=image
