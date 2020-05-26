from ledfx.devices import Device
import logging
import voluptuous as vol
import numpy as np
import socket

_LOGGER = logging.getLogger(__name__)

class FXMatrix(Device):
    """FXMatrix device support"""

    CONFIG_SCHEMA = vol.Schema({
        vol.Required('ip_address', description='Hostname or IP address of the device'): str,
        vol.Required('port', description='Port for the UDP device'): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
    })

    def activate(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super().activate()

    def deactivate(self):
        super().deactivate()
        self._sock = None

    def flush(self, data):
        udpData = bytearray()
        byteData = data.astype(np.dtype('B'))
        # Append all of the pixel data
        udpData.extend(byteData.flatten().tobytes())

        self._sock.sendto(bytes(udpData), (self._config['ip_address'], self._config['port']))