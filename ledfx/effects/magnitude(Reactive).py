from ledfx.effects.audio import AudioReactiveEffect, FREQUENCY_RANGES
from ledfx.effects.gradient import GradientEffect
import voluptuous as vol
import numpy as np


class MagnitudeAudioEffect(AudioReactiveEffect, GradientEffect):

    NAME = "Magnitude"
    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "frequency_range",
                description="Frequency range for the beat detection",
                default="bass",
            ): vol.In(list(FREQUENCY_RANGES.keys())),
        }
    )

    def config_updated(self, config):
        self._frequency_range = np.linspace(
            FREQUENCY_RANGES[self.config["frequency_range"]].min,
            FREQUENCY_RANGES[self.config["frequency_range"]].max,
            20,
        )

    def audio_data_updated(self, data):

        # Grab the filtered and interpolated melbank data
        magnitude = np.max(data.sample_melbank(list(self._frequency_range)))
        if magnitude > 1.0:
            magnitude = 1.0
        self.pixels = self.apply_gradient(magnitude)
