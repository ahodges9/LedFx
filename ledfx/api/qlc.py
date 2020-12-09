from ledfx.config import save_config
from ledfx.api import RestEndpoint
from ledfx.api.websocket import WebsocketConnection
from ledfx.utils import generate_id
from aiohttp import web
import logging
import json

_LOGGER = logging.getLogger(__name__)

class QLCEndpoint(RestEndpoint):
    """REST end-point for querying and managing QLC webhook"""

    ENDPOINT_PATH = "/api/qlc"

    async def get(self) -> web.Response:
        """Get status of QLC webhook"""
        response = self._ledfx.config.get('qlc')
        # response = {
        #     'status' : 'success' ,
        #     'qlc_enabled' : # is qlc integration enabled?,
        #     'qlc_ip' : # ip address for qlc?
        #     'qlc_webhook_status' : # is the webhook connected?,
        # }
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

##### From here is copy of scenes api

    async def delete(self, request) -> web.Response:
        """Disable QLC webhook"""
        data = await request.json()

        scene_id = data.get('id')
        if scene_id is None:
            response = { 'status' : 'failed', 'reason': 'Required attribute "scene_id" was not provided' }
            return web.json_response(data=response, status=500)

        if not scene_id in self._ledfx.config['scenes'].keys():
            response = { 'status' : 'failed', 'reason': 'Scene {} does not exist'.format(scene_id) }
            return web.json_response(data=response, status=500)
        
        # Delete the scene from configuration
        del self._ledfx.config['qlc'][scene_id]

        # Save the config
        save_config(
            config = self._ledfx.config, 
            config_dir = self._ledfx.config_dir)

        response = { 'status' : 'success' }
        return web.json_response(data=response, status=200)

    async def put(self, request) -> web.Response:
        """Update QLC webhook IP address"""
        data = await request.json()


        scene = self._ledfx.config['scenes'][scene_id]

        if action == "activate":
            for device in self._ledfx.devices.values():
                # Check device is in scene, make no changes if it isn't
                if not device.id in scene['devices'].keys():
                    _LOGGER.info(('Device with id {} has no data in scene {}').format(device.id, scene_id))
                    continue

                # Set effect of device to that saved in the scene,
                # clear active effect of device if no effect in scene
                if scene['devices'][device.id]:
                    # Create the effect and add it to the device
                    effect = self._ledfx.effects.create(
                        ledfx = self._ledfx,
                        type = scene['devices'][device.id]['type'],
                        config = scene['devices'][device.id]['config'])
                    device.set_effect(effect)
                else:
                    device.clear_effect()

        elif action == "rename":
            name = data.get('name')
            if name is None:
                response = { 'status' : 'failed', 'reason': 'Required attribute "name" was not provided' }
                return web.json_response(data=response, status=500)

            # Update and save config
            self._ledfx.config['scenes'][scene_id]['name'] = name
            save_config(
                config = self._ledfx.config, 
                config_dir = self._ledfx.config_dir)

        response = { 'status' : 'success' }
        return web.json_response(data=response, status=200)

    async def post(self, request) -> web.Response:
        """Activate QLC webhook"""
        data = await request.json()

        scene_name = data.get('name')
        if scene_name is None:
            response = { 'status' : 'failed', 'reason': 'Required attribute "scene_name" was not provided' }
            return web.json_response(data=response, status=500)

        scene_id = generate_id(scene_name)

        scene_config = {}
        scene_config['name'] = scene_name
        scene_config['devices'] = {}
        for device in self._ledfx.devices.values():
            effect = {}
            if device.active_effect:
                effect['type'] = device.active_effect.type
                effect['config'] = device.active_effect.config
                #effect['name'] = device.active_effect.name
            scene_config['devices'][device.id] = effect

        # Update the scene if it already exists, else create it
        self._ledfx.config['scenes'][scene_id] = scene_config 

        save_config(
            config = self._ledfx.config, 
            config_dir = self._ledfx.config_dir)
        
        response = { 'status' : 'success', 'qlc_enabled' : enable_qlc}
        return web.Response(text=json.dumps(response), status=200)
