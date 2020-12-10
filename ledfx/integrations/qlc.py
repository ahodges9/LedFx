from ledfx.utils import RegistryLoader
from ledfx.events import Event
from ledfx.integrations import Integration
import aiohttp
import asyncio
import voluptuous as vol
import numpy as np
import importlib
import pkgutil
import logging
import time
import os
import re

_LOGGER = logging.getLogger(__name__)


class QLC(Integration):
    """QLC+ Integration"""
    _status = None

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Required(
                "name",
                description="Name of this integration",
                default="QLC+"
            ): str,
            vol.Required(
                "description",
                description="Description of this integration",
                default="Web Api Integration for Q Light Controller Plus"
            ): str,
            vol.Required(
                "ip_address",
                description="QLC+ ip address",
                default="127.0.0.1"
            ): str,
            vol.Required(
                "port",
                description="QLC+ port",
                default=9999
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
        }
    )

    def __init__(self, ledfx, config):
        super().__init__(ledfx, config)

        self._connection = None

        def send_payload(e):
            print(f"Heard event {e}")
            self.send_package(e)

        self._ledfx.events.add_listener(
            send_payload, Event.SCENE_SET)

    async def callback(self, msg):
        print(msg)

    async def send(self, msg):
        await self._ws.send_str(msg)

    async def connect(self):
        print("BITCONNEEEEEECT")
        addr = ":".join((self._config['ip_address'], str(self._config['port'])))
        async with aiohttp.ws_connect(addr) as self._ws:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.callback(msg)
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

    def disconnect(self):
        if self._ws is not None:
            self._ws.close()

    def send_package(self, e):
        print(e)