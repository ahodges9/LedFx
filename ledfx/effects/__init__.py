from ledfx.utils import BaseRegistry, RegistryLoader
#from ledfx.effects.audio import FREQUENCY_RANGES
from functools import lru_cache
from PIL import ImageFilter, Image, ImageOps, ImageEnhance, ImageChops
import voluptuous as vol
import numpy as np
import importlib
import colorsys
import pkgutil
import logging
import sys
import os

_LOGGER = logging.getLogger(__name__)

def mix_colors(color_1, color_2, ratio):
    if color_2 == []:
        return (color_1[0] * (1-ratio) + 0,
                color_1[1] * (1-ratio) + 0,
                color_1[2] * (1-ratio) + 0)
    else:
        return (color_1[0] * (1-ratio) + color_2[0] * ratio,
                color_1[1] * (1-ratio) + color_2[1] * ratio,
                color_1[2] * (1-ratio) + color_2[2] * ratio)

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

def fill_rainbow(pixels, initial_hue, delta_hue):
    hue = initial_hue
    sat = 0.95
    val = 1.0
    for y in range(0, pixels.height):
        for x in range(0, pixels.width):
            pixels.putpixel((x, y), hsv2rgb(hue, sat, val))
            hue = hue + delta_hue
    return pixels

@BaseRegistry.no_registration
class Effect(BaseRegistry):
    """
    Manages an effect
    """
    NAME = ""
    _image = None
    _dirty = False
    _config = None
    _active = False
    _dimensions = (0, 0)

    # Basic effect properties that can be applied to all effects
    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('blur', description='Amount to blur the effect', default=0.0): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=10)),
        vol.Optional('flip', description='Flip the effect', default=False): bool,
        vol.Optional('mirror', description='Mirror the effect', default=False): bool,
        vol.Optional('brightness', description='Brightness of strip', default=1.0): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=10.0)),
    })

    def __init__(self, ledfx, config):
        self._ledfx = ledfx
        self._dirty_callback = None
        self.update_config(config)

    def __del__(self):
        if self._active:
            self.deactivate()

    def activate(self, dimensions):
        """Attaches an output channel to the effect"""
        self._dimensions = dimensions
        self._image = Image.new("RGB", dimensions)
        self._active = True
    
        # Iterate all the base classes and check to see if there is a custom
        # implementation of config updates. If to notify the base class.
        valid_classes = list(type(self).__bases__)
        valid_classes.append(type(self))
        for base in valid_classes:
            if base.activated != super(base, base).activated:
                base.activated(self)

        _LOGGER.info("Effect {} activated.".format(self.NAME))

    def deactivate(self):
        """Detaches an output channel from the effect"""
        self._image = None
        self._active = False

        _LOGGER.info("Effect {} deactivated.".format(self.NAME))

    def update_config(self, config):
        # TODO: Sync locks to ensure everything is thread safe
        validated_config = type(self).schema()(config)
        self._config = validated_config

        def inherited(cls, method):
            if hasattr(cls, method) and hasattr(super(cls, cls), method):
                return cls.foo == super(cls).foo
            return False

        # Iterate all the base classes and check to see if there is a custom
        # implementation of config updates. If to notify the base class.
        valid_classes = list(type(self).__bases__)
        valid_classes.append(type(self))
        for base in valid_classes:
            if base.config_updated != super(base, base).config_updated:
                base.config_updated(self, self._config)

        _LOGGER.info("Effect {} config updated to {}.".format(
            self.NAME, validated_config))

    def config_updated(self, config):
        """
        Optional event for when an effect's config is updated. This
        should be used by the subclass only if they need to build up
        complex properties off the configuration, otherwise the config
        should just be referenced in the effect's loop directly
        """
        pass

    def activated(self):
        """
        Optional event if an effect was activated
        """
        pass

    @property
    def is_active(self):
        """Return if the effect is currently active"""
        return self._active

    @property
    def is_2d(self):
        """Return if the effect is a matrix"""
        return self._dimensions[1] > 1

    @property
    def outputimage(self):
        input = self.image

        # Apply some of the base output filters if necessary
        if self._config['brightness']:
            enhancer = ImageEnhance.Brightness(input)
            input = enhancer.enhance(self._config['brightness'])
        if self._config['blur'] != 0.0:
            input = input.filter(ImageFilter.GaussianBlur(
                radius=self._config['blur']))

        # horizontal flip
        if self._config['flip']:
            input = ImageOps.mirror(input)

        # reflection effect
        if self._config['mirror']:
            # Scale image to half width
            hImage = input.resize(
                (int(self._dimensions[0] / 2), self._dimensions[1]), resample=3)

            input.paste(hImage, (0, 0))
            input.paste(ImageOps.mirror(hImage),
                        (int(self._dimensions[0] / 2), 0))

        return input

    @property
    def image(self):
        """Returns the pixels for the channel"""
        if not self._active:
            raise Exception(
                'Attempting to access image before effect is active')

        return self._image

    @image.setter
    def image(self, input):
        """Sets the pixels for the channel"""
        if not self._active:
            _LOGGER.warning(
                'Attempting to set image before effect is active. Dropping.')
            return
        self._image = input
        self._dirty = True

        if self._dirty_callback:
            self._dirty_callback()

    def setDirtyCallback(self, callback):
        self._dirty_callback = callback

    @property
    def name(self):
        return self.NAME

@BaseRegistry.no_registration
class Effect1D(Effect):
    """This upgrades 1D effects for use with 2d LED arrays."""

    _pixels = None

    def activate(self, dimensions):
        super().activate(dimensions)
        self._pixels = Image.new("RGB", (dimensions[0], 1))

    @property
    def pixel_count(self):
        """Returns the number of pixels for the channel"""
        return self._dimensions[0]

    @property
    def pixels(self):
        """Returns the pixels for the channel"""
        if not self._active:
            raise Exception(
                'Attempting to access pixels before effect is active')

        return self._pixels.copy()

    @pixels.setter
    def pixels(self, pixels):
        """Transform pixels to 2d matrix"""

        self._pixels = pixels

        # Filter and update the pixel values
        if self.is_2d:
            temp = ImageChops.offset(self.image, 0, 1) # scroll down 1 pixel

            # add new values at the top
            temp.paste(pixels, (0, 0))
            
            self.image = temp
        else:
            self.image = pixels


class Effects(RegistryLoader):
    """Thin wrapper around the effect registry that manages effects"""

    PACKAGE_NAME = 'ledfx.effects'

    def __init__(self, ledfx):
        super().__init__(ledfx=ledfx, cls=Effect, package=self.PACKAGE_NAME)
        self._ledfx.audio = None
