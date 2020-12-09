from ledfx.effects.audio import AudioReactiveEffect
from ledfx.effects.gradient import GradientEffect
from ledfx.color import GRADIENTS
import voluptuous as vol
import numpy as np


class MultiBarAudioEffect(AudioReactiveEffect, GradientEffect):

    NAME = "Multicolor Bar"
    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional(
                "gradient_name",
                description="Color scheme to cycle through",
                default="Rainbow",
            ): vol.In(list(GRADIENTS.keys())),
            vol.Optional(
                "mode",
                description="Choose from different animations",
                default="wipe",
            ): vol.In(list(["cascade", "wipe"])),
            vol.Optional(
                "ease_method",
                description="Acceleration profile of bar",
                default="linear",
            ): vol.In(list(["ease_in_out", "ease_in", "ease_out", "linear"])),
            vol.Optional(
                "color_step",
                description="Amount of color change per beat",
                default=0.125,
            ): vol.All(vol.Coerce(float), vol.Range(min=0.0625, max=0.5)),
        }
    )

    def config_updated(self, config):
        self.phase = 0
        self.color_idx = 0

    def audio_data_updated(self, data):
        # Run linear beat oscillator through easing method
        beat_oscillator, beat_now = data.oscillator()
        if self._config["ease_method"] == "ease_in_out":
            x = 0.5 * np.sin(np.pi * (beat_oscillator - 0.5)) + 0.5
        elif self._config["ease_method"] == "ease_in":
            x = beat_oscillator ** 2
        elif self._config["ease_method"] == "ease_out":
            x = -((beat_oscillator - 1) ** 2) + 1
        elif self._config["ease_method"] == "linear":
            x = beat_oscillator

        # Colour change and phase
        if beat_now:
            self.phase = 1 - self.phase  # flip flop 0->1, 1->0
            # 8 colours, 4 beats to a bar
            self.color_idx += self._config["color_step"]
            self.color_idx = self.color_idx % 1  # loop back to zero

        color_fg = self.get_gradient_color(self.color_idx)
        color_bkg = self.get_gradient_color(
            (self.color_idx + self._config["color_step"]) % 1
        )

        # Compute position of bar start and stop
        if self._config["mode"] == "wipe":
            if self.phase == 0:
                idx = x
            elif self.phase == 1:
                idx = 1 - x
                color_fg, color_bkg = color_bkg, color_fg

        elif self._config["mode"] == "cascade":
            idx = x

        # Construct the array
        p = np.zeros(np.shape(self.pixels))
        p[: int(self.pixel_count * idx), :] = color_bkg
        p[int(self.pixel_count * idx) :, :] = color_fg
        # Update the pixel values
        self.pixels = p
