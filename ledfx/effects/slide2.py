from ledfx.effects.audio import AudioReactiveEffect, FREQUENCY_RANGES_SIMPLE, MIN_MIDI, MAX_MIDI
from ledfx.effects.gradient import GradientEffect
from ledfx.effects.math import ExpFilter
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
        #vol.Optional('fade_rate', description='Rate at which notes fade', default = 0.15):  vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
        #vol.Optional('responsiveness', description='Responsiveness of the note changes', default = 0.15):  vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
    })

    def config_updated(self, config):
        self.bands = np.zeros(self._config["resolution"])
        self.band_smoothing = ExpFilter(np.tile(1e-1, self._config["resolution"]), alpha_decay=0.2, alpha_rise=0.9)


    def audio_data_updated(self, data):
        # Populate octave and note data
        data.melbank()
        # Get octave and note data
        octave = data.averaged_octave
        # Split octave into bins, find max value per bin
        maxed_bins = [i.max() for i in np.array_split(octave, self._config["resolution"])]
        # Update colour bands with max from each octave bin
        self.bands = self.band_smoothing.update(maxed_bins)

        # TODO move to config_updated, when pixel count is known during effect setup
        # Get colours from band indexes (scaled between 0 and 1)
        self.colours = np.array([self.get_gradient_color(i) for i in np.linspace(0, 1, self._config["resolution"])]).astype(int)

        #note_heights = octave[notes]
        total_height = self.bands.sum()
        # Scale note heights up to length of strip
        bands = self.pixel_count * (self.bands / total_height)
        # print(bands, bands.sum())
        # Make empty array, split into sectons to fill with colour
        new_pixels = np.array(np.array_split(np.zeros((224, 3)), np.cumsum(bands[:-1]).astype(int), axis=0))
        # Assign pixel colours 
        for i in range(self._config["resolution"]):
            new_pixels[i][:] = self.colours[i]

        # Join together colour blocks
        new_pixels = np.vstack(new_pixels)
        # Set the pixels
        self.pixels = new_pixels


        # y = data.interpolated_melbank(self.pixel_count, filtered = False)
        # midi_value = self.pitch_o(data.audio_sample())[0]
        # note_color = COLORS['black']

        # if not self.avg_midi:
        #     self.avg_midi = midi_value

        # # Average out the midi values to be a little more stable
        # if midi_value >= MIN_MIDI:
        #     self.avg_midi = self.avg_midi * (1.0 - self._config['responsiveness']) + midi_value * self._config['responsiveness']

        # # Grab the note color based on where it falls in the midi range
        # if self.avg_midi >= MIN_MIDI:
        #     midi_scaled = (self.avg_midi - MIN_MIDI) / (MAX_MIDI - MIN_MIDI)
        #     note_color = self.get_gradient_color(midi_scaled)

        # # Mix in the new color based on the filterbank information and fade out
        # # the old colors
        # new_pixels = self.pixels
        # for index in range(self.pixel_count):
        #     new_color = mix_colors(self.pixels[index], note_color, y[index])
        #     new_color = mix_colors(new_color, COLORS['black'], self._config['fade_rate'])
        #     new_pixels[index] = new_color

        # # Set the pixels
        # self.pixels = new_pixels
