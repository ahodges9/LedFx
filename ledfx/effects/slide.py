from ledfx.effects.audio import AudioReactiveEffect, FREQUENCY_RANGES_SIMPLE, MIN_MIDI, MAX_MIDI
from ledfx.effects.gradient import GradientEffect
from ledfx.effects.math import ExpFilter, TemporalFilter
from ledfx.effects import mix_colors
from ledfx.color import COLORS
from ledfx.events import GraphUpdateEvent
import voluptuous as vol
import numpy as np
import aubio
import math

class Slide2AudioEffect(AudioReactiveEffect, GradientEffect):

    NAME = "Slide2"

    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('blur', description='Amount to blur the effect', default = 1.0): vol.Coerce(float),
        vol.Optional('mirror', description='Mirror the effect', default = True): bool,
        vol.Optional('resolution', description='Number of colour bands', default = 7): vol.All(vol.Coerce(int), vol.Range(min=3, max=10)),
        vol.Optional('responsiveness', description='Responsiveness to the note changes', default = 0.03):  vol.All(vol.Coerce(float), vol.Range(min=0.01, max=0.1)),
    })

    def config_updated(self, config):
        self.bands = np.zeros(self._config["resolution"])
        self.band_smoothing = ExpFilter(np.tile(1e-1, self._config["resolution"]), alpha_decay=0.05, alpha_rise=0.9)
        self.temporal_filter = None


    def audio_data_updated(self, data):
        # TODO move to config_updated when self.pixel_count at that point
        if not self.temporal_filter:
            self.temporal_filter = TemporalFilter(self.pixels, rise=self._config["responsiveness"], decay=0.1)

        # Populate octave data
        data.calc_octaves()
        # Get octave data
        octave = data.averaged_octave
        # Split octave into bins, find max value per bin
        maxed_bins = [i.max() for i in np.array_split(octave, self._config["resolution"])]
        # Get colours from band indexes (scaled between 0 and 1)
        self.colours = np.array([self.get_gradient_color(i) for i in np.linspace(0, self.pixel_count-1, self._config["resolution"]).astype(int)])
        # Update colour bands with max from each octave bin
        self.bands = self.band_smoothing.update(maxed_bins)
        total_height = self.bands.sum()
        # Scale note heights up to length of strip
        bands = self.pixel_count * (self.bands / total_height)
        # Make empty array, split into sectons of scaled note length to fill with colour of each note
        new_pixels = np.array(np.array_split(np.zeros(np.shape(self.pixels)), np.cumsum(bands[:-1]).astype(int), axis=0))
        # Assign pixel colours 
        for i in range(self._config["resolution"]):
            new_pixels[i][:] = self.colours[i]

        # Join together colour blocks
        new_pixels = np.vstack(new_pixels)
        # Set the pixels
        self.pixels = self.temporal_filter.update(new_pixels)
