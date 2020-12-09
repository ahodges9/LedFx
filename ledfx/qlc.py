from ledfx.utils import RegistryLoader
from ledfx.events import Event
from ledfx.api.websocket import WebsocketConnection
import voluptuous as vol
import numpy as np
import importlib
import pkgutil
import logging
import time
import os
import re

_LOGGER = logging.getLogger(__name__)


class QLC(RegistryLoader):
    """Thin wrapper around the device registry that manages devices"""

    PACKAGE_NAME = 'ledfx.qlc'

    def __init__(self, ledfx):
        super().__init__(ledfx, self.PACKAGE_NAME)

        def send_payload(e):
            self.send_package(e)

        self._ledfx.events.add_listener(
            send_payload, Event.SCENE_SET)

    def send_package(self, e):
        print(e)

    # def create_from_config(self, config):
    #     for device in config:
    #         _LOGGER.info("Loading device from config: {}".format(device))
    #         self._ledfx.devices.create(
    #             id = device['id'],
    #             type = device['type'],
    #             config = device['config'],
    #             ledfx = self._ledfx)
    #         if 'effect' in device:
    #             try:
    #                 effect = self._ledfx.effects.create(
    #                     ledfx = self._ledfx,
    #                     type = device['effect']['type'],
    #                     config = device['effect']['config'])
    #                 self._ledfx.devices.get_device(device['id']).set_effect(effect)
    #             except vol.MultipleInvalid:
    #                 _LOGGER.warning('Effect schema changed. Not restoring effect')
                

    # def clear_all_effects(self):
    #     for device in self.values():
    #         device.clear_effect()

    # def get_device(self, device_id):
    #     for device in self.values():
    #         if device_id == device.id:
    #             return device
    #     return None
