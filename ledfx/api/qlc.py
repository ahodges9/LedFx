from ledfx.config import save_config
from ledfx.api import RestEndpoint
from aiohttp import web
import logging
import json

_LOGGER = logging.getLogger(__name__)

class qlcEndpoint(RestEndpoint):

    ENDPOINT_PATH = "/api/qlc"

    async def get(self) -> web.Response:
        response = self._ledfx.config.get('qlc')

        return web.Response(text=json.dumps(response), status=200)

    async def put(self, request) -> web.Response:
        qlc = self._ledfx.config.get('qlc')
        if qlc is None:
            response = { 'not found': 404 }
            return web.Response(text=json.dumps(response), status=404)

        data = await request.json()
        enable_qlc = data.get('qlc_enabled')
        if enable_qlc is None:
            response = { 'status' : 'failed', 'reason': 'Required attribute "enable" was not provided' }
            return web.Response(text=json.dumps(response), status=500)


        # Update and save the configuration
        self._ledfx.config['qlc'] = enable_qlc

        save_config(
            config = self._ledfx.config, 
            config_dir = self._ledfx.config_dir)

        response = { 'status' : 'success', 'qlc_enabled' : enable_qlc}
        return web.Response(text=json.dumps(response), status=200)