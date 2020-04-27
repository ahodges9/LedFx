from ledfx.effects.temporal import TemporalEffect
from ledfx.effects import fill_rainbow
from ledfx.color import RGB
from PIL import Image
import voluptuous as vol
import os, sys
import numpy as np

class ShowImage(TemporalEffect):

    NAME = "Show Image"
    CONFIG_SCHEMA = vol.Schema({
    })

    _time = 0.0
#    _images = []
    _input = Image.open("144.gif").convert('RGBA')
    _input.thumbnail((14,14))
    _image = Image.new("RGB", _input.size, (0,0,0)) # black background
    _image.paste(_input, (0, 0), _input) 

    def effect_loop(self):
        self.pixels = np.array(self._image.getdata(),  dtype=float)
