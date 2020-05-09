from ledfx.effects.temporal import TemporalEffect
from PIL import Image
import voluptuous as vol
import os
import sys
import math
import numpy as np


class ShowImage(TemporalEffect):

    NAME = "Show Image"
    CONFIG_SCHEMA = vol.Schema({
    })
    _images = []
    _time = 0.0
    _currentFrame = 99999

    def config_updated(self, config):
        #self._config = self.AUDIO_CONFIG_SCHEMA(config)
        self.load_images("t4518.gif")

    def load_images(self, imagepath):
        _images = []
        _input = Image.open(imagepath)

        for frame in range(0, _input.n_frames):
            _input.seek(frame)

            # Scale the image
            _input.thumbnail(self._dimensions, Image.NEAREST)  # Image.ANTIALIAS

            # background color
            _image = Image.new("RGB", this._dimensions, (255, 255, 255))

            # paste the image on the center of a new image with a background color
            x1 = int(math.floor((_image.width - _input.width) / 2))
            y1 = int(math.floor((_image.height - _input.height) / 2))

            _image.paste(_input, (x1, y1), _input.convert('RGBA'))
            _image.info = _input.info  # contains duration info

            _images.append(_image)

        self._images = _images

    def effect_loop(self):
        self._time = self._time+0.01

        newFrame = self._currentFrame

        if newFrame < 0 or newFrame >= len(self._images):
            self._time = 0
            newFrame = 0

        if len(self._images) > 0:
            if self._time > self._images[newFrame].info["duration"]/1000.0:
                self._time = 0
                newFrame = newFrame+1

            if newFrame >= len(self._images):
                newFrame = 0

        if newFrame != self._currentFrame:
            self._currentFrame = newFrame
            self.image = self._images[self._currentFrame]
