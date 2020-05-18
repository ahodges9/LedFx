from ledfx.effects.temporal import TemporalEffect
from ledfx.effects.animations import ANIMATION_LIST
from PIL import Image
import voluptuous as vol
import os
import sys
import math
import numpy as np


class ShowImage(TemporalEffect):
    NAME = "Show Image"
    CONFIG_SCHEMA = vol.Schema({
        vol.Required('image_name', description='image', default="144.gif"): vol.In(list(ANIMATION_LIST)),
    })
    _images = []
    _time = 0.0
    _currentFrame = -1

    def config_updated(self, config):
        self.load_images()

    def activated(self):
        self.load_images()

    def load_images(self):
        if self._dimensions[0] <= 0:
            return

        animation_path = os.path.join(os.path.dirname(
            __file__), "animations/" + self.config['image_name'])
        _images = []
        _input = Image.open(animation_path)

        for frame in range(0, _input.n_frames):
            _input.seek(frame)

            # Scale the image
            # Image.ANTIALIAS
            _input.thumbnail(self._dimensions, Image.NEAREST)

            # background color
            _image = Image.new("RGB", self._dimensions, (255, 255, 255))

            # paste the image on the center of a new image with a background color
            x1 = int(math.floor((_image.width - _input.width) / 2))
            y1 = int(math.floor((_image.height - _input.height) / 2))

            _image.paste(_input, (x1, y1), _input.convert('RGBA'))
            _image.info = _input.info  # contains duration info

            _images.append(_image)

        self._images = _images
        _currentFrame = -1
        _time = 0

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
