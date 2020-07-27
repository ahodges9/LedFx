from ledfx.effects import Effect
from ledfx.color import COLORS
from ledfx.color import GRADIENTS
import time
import logging
import voluptuous as vol
import numpy as np
import random

_LOGGER = logging.getLogger(__name__)
_rate = 60

@Effect.no_registration
class ModulateEffect(Effect):
    """
    Extension of TemporalEffect that applies brightness modulation
    over the strip. This is intended to allow more static effects like
    Gradient or singleColor to have some visual movement.
    """
    # _thread_active = False
    # _thread = None
    
    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('modulate', description='Brightness modulation', default = False): bool,
        vol.Optional('modulation_effect', default = "sine", description="Choose an animation"): vol.In(list(["sine", "breath"])),
        vol.Optional('modulation_speed', default = 0.1, description="Animation speed"): vol.All(vol.Coerce(float), vol.Range(min=0.01, max=1))
    })

    def config_updated(self, config):
        self._counter = 0

        # temporal array for breathing cycle
        self._breath_cycle = np.linspace(0,9,9*_rate)
        self._breath_cycle[:3*_rate] = 0.4 * np.sin(self._breath_cycle[:3*_rate]-(np.pi/2)) + 0.6
        self._breath_cycle[3*_rate:] = np.exp(3-self._breath_cycle[3*_rate:]) + 0.2


    def modulate(self, pixels):
        """
        Call this function from the effect
        """
        if not self._config["modulate"]:
            return pixels

        if self._config["modulation_effect"] == "sine":
            self._counter += 0.4 * self._config["modulation_speed"] / np.pi
            if self._counter >= 15:
             self._counter = 0      
            # overlay = np.linspace(self._counter + np.pi,
            #                       self._counter,
            #                       self.pixel_count)\
            # overlay = np.tile(np.sin(overlay)+0.4, (3,1)).T
            print(self._counter)
            if self._counter >= 0 and self._counter <= 6:
             self.color = np.array(COLORS["red"], dtype=float)
             overlay = np.linspace(self._counter + np.pi,
                                   random.randint(200,500),
                                   self.pixel_count)
             overlay = np.tile(np.tan(overlay), (3, 1)).T
            elif self._counter >= 6 and self._counter <= 15:
             self.color = np.array(COLORS["magenta"], dtype=float)
             overlay = np.linspace(self._counter + np.pi,
                                    random.randint(0,100),
                                    self.pixel_count)
             overlay = np.tile(np.sin(overlay), (3, 1)).T
            return pixels * overlay

        elif self._config["modulation_effect"] == "breath":
            self._counter += self._config["modulation_speed"]
            if self._counter == 9*_rate:
                self._counter = 0

            pixels[int(self._breath_cycle[int(self._counter)] * self.pixel_count):, :] = 0
            return pixels

        else:
            # LOG that unknown mode selected somehow?
            return pixels