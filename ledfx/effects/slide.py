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

class SlideAudioEffect(AudioReactiveEffect, GradientEffect):

    NAME = "Slide"

    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('blur', description='Amount to blur the effect', default = 1.0): vol.Coerce(float),
        vol.Optional('mirror', description='Mirror the effect', default = True): bool,
        vol.Optional('resolution', description='Number of colour bands', default = 7): vol.All(vol.Coerce(int), vol.Range(min=3, max=10)),
        #vol.Optional('fade_rate', description='Rate at which notes fade', default = 0.15):  vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
        #vol.Optional('responsiveness', description='Responsiveness of the note changes', default = 0.15):  vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
    })

    def config_updated(self, config):
        self.n_pixels = 224

    def audio_data_updated(self, data):
        # Populate octave and note data
        data.melbank()
        # Get octave and note data
        octave = data.averaged_octave
        notes = data.notes
        if not notes.size:
            self.pixels *= 0.98
            return

        note_heights = octave[notes]
        total_height = note_heights.sum()
        # Scale note heights up to length of strip
        note_heights *= self.n_pixels / total_height
        # Scale note indexes between 0 and 1 
        notes = np.divide(notes, octave.size)
        notes = notes - notes % (1 / self._config["resolution"])
        # Get colours from scaled note indexes
        colours = np.array([self.get_gradient_color(i) for i in notes]).astype(int)
        # Make empty array, split into sectons to fill with colour
        new_pixels = np.array(np.split(np.zeros((self.n_pixels, 3)), np.cumsum(note_heights[:-1]).astype(int)))
        # Assign pixel colours 
        for i in range(new_pixels.shape[0]):
            new_pixels[i][:] = colours[i]
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
