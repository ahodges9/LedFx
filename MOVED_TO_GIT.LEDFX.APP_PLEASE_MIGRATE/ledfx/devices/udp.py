from ledfx.devices import Device
import logging
import voluptuous as vol
import numpy as np
import socket

_LOGGER = logging.getLogger(__name__)

class UDPDevice(Device):
    """Generic UDP device support"""

    CONFIG_SCHEMA = vol.Schema({
        vol.Required('ip_address', description='Hostname or IP address of the device'): str,
        vol.Required('port', description='Port for the UDP device'): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
        vol.Required('pixel_count', description='Number of individual pixels'): vol.All(vol.Coerce(int), vol.Range(min=1)),
        vol.Optional('include_indexes', description='Include the index for every LED', default=False): bool,
        vol.Optional('data_prefix', description='Data to be appended in hex format'): str,
        vol.Optional('data_postfix', description='Data to be prepended in hex format'): str,
    })

    def activate(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super().activate()

    def deactivate(self):
        super().deactivate()
        self._sock = None

    @property
    def pixel_count(self):
        return int(self._config['pixel_count'])

    def flush(self, data):
        udpData = bytearray()
        byteData = data.astype(np.dtype('B'))
    
        # Append the prefix if provided
        prefix = self._config.get('data_prefix')
        if prefix:
            udpData.extend(bytes.fromhex(prefix))

        # Append all of the pixel data
        if self._config['include_indexes']:
            for i in range(len(byteData)):
                udpData.extend(bytes([i]))
                udpData.extend(byteData[i].flatten().tobytes())
        else:
            udpData.extend(byteData.flatten().tobytes())

        # Append the postfix if provided
        postfix = self._config.get('data_postfix')
        if postfix:
            udpData.extend(bytes.fromhex(postfix))

        self._sock.sendto(bytes(udpData), (self._config['ip_address'], self._config['port']))