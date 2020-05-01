from ledfx.effects.temporal import TemporalEffect
from ledfx.effects.fonts import FONT_LIST
from ledfx.color import COLORS

from PIL import Image, ImageFont, ImageDraw
import voluptuous as vol
import os
import sys
import math
import numpy as np


class Text(TemporalEffect):

    NAME = "Text"
    CONFIG_SCHEMA = vol.Schema({
        vol.Required('text', description='Text to display', default="Lorem Ipsum"): vol.Coerce(str),
        vol.Optional('font_size', description='Size of the font', default=6): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
        vol.Optional('font_name', description='Font', default="Berkelium1541.ttf"): vol.In(list(FONT_LIST)),
        vol.Optional('font_antialias', description='Use antialising', default=False): bool,
        vol.Optional('text_color', description='Text color', default='white'): vol.In(list(COLORS.keys())),
        vol.Optional('bg_color', description='Background color', default='red'): vol.In(list(COLORS.keys())),
    })

    _time = 0.0

    def config_updated(self, config):
        fontpath = os.path.join(os.path.dirname(
            __file__), "fonts/" + config['font_name'])
        font = ImageFont.truetype(fontpath, config['font_size'])

        # determine pixel size of our text
        self._size = font.getsize(config['text'])

        # render text to a transparent image that may be larger than the display
        self._fontimage = Image.new("RGBA", self._size)

        draw = ImageDraw.Draw(self._fontimage)
        if not config['font_antialias']:
            draw.fontmode = "1"  # disable antialiasing

        draw.text((0, 0), config['text'], font=font, fill=config['text_color'])
        _time = 0
        return

    def effect_loop(self):
        self._time = self._time+0.01

        # background color
        _image = Image.new("RGB", (14, 14), self.config['bg_color'])

        xoffset = int(self._time) % (self._size[0]+2*14)

        _image.paste(self._fontimage, (14-xoffset, 0), self._fontimage.convert('RGBA'))
       
        self.pixels = np.array(_image.getdata(), dtype=float)
