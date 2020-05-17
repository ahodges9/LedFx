from ledfx.effects.audio import AudioReactiveEffect
from ledfx.color import COLORS
from PIL import Image, ImageDraw
import voluptuous as vol
import numpy as np
import math 

class Strobe(AudioReactiveEffect):
    NAME = "Scope"
    CONFIG_SCHEMA = vol.Schema({
    })

    def config_updated(self, config):
        return

    def audio_data_updated(self, data):
        samples = data.audio_sample(raw=True)

        # Get curve from sample data
        dx = len(samples)/self._dimensions[0]
        arr = []
        for x in range(0, self._dimensions[0]):
            arr.append(np.mean(samples[int(x*dx):int((x+1)*dx)]))

        # determine scaling factor
        dy = self._dimensions[1] / max(max(map(abs, arr)), 0.1) / 2

        # draw curve
        image = Image.new("RGB", self._dimensions, color=0)
        img1 = ImageDraw.Draw(image)
        for x in range(1, self._dimensions[0]):
            img1.line(((x-1, int(arr[x-1]*dy+self._dimensions[1]/2)), (x, arr[x]*dy+self._dimensions[1]/2)), width=1)

        # output image
        self.image = image
