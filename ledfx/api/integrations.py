from ledfx.config import save_config
from ledfx.api import RestEndpoint
from ledfx.api.websocket import WebsocketConnection
from ledfx.utils import generate_id
from aiohttp import web
import logging
import json

_LOGGER = logging.getLogger(__name__)

class IntegrationsEndpoint(RestEndpoint):
    """REST end-point for querying and managing QLC webhook"""

    ENDPOINT_PATH = "/api/integrations"

    async def get(self) -> web.Response:
        """Get info of all integrations"""
        response = {"status": "success", "integrations": {}}
        for integration in self._ledfx.integrations.values():
            response["integrations"][integration.id] = {
                "id": integration.id,
                "type": integration.type,
                "status": integration.status,
                "config": integration.config
            }
        return web.Response(text=json.dumps(response), status=200)

    async def put(self, integration_id) -> web.Response:
        """Toggle an integration on or off"""
        integration = self._ledfx.integrations.get(integration_id)
        if integration is None:
            response = { 'not found': 404 }
            return web.Response(text=json.dumps(response), status=404)

        # Toggle the integration
        active = integration.active
        
        if not active:
            integration.activate()
        else:
            integration.deactivate()

        # Update and save the configuration
        for integration in self._ledfx.config["integrations"]:
            if integration["id"] == integration.id:
                integration["active"] = not active
                break
        save_config(
            config=self._ledfx.config,
            config_dir=self._ledfx.config_dir,
        )

        response = {"status": "success"}
        return web.json_response(data=response, status=200)

    async def delete(self, integration_id) -> web.Response:
        """Delete an integration, erasing all its configuration
        NOTE: THIS DOES NOT TURN OFF THE INTEGRATION, IT DELETES IT!"""
        integration = self._ledfx.integrations.get(integration_id)
        if integration is None:
            response = { 'not found': 404 }
            return web.Response(text=json.dumps(response), status=404)

        # Delete the integration from configuration
        del self._ledfx.config['integrations'][integration.id]

        # Delete the integration itself
        del integration

        # Save the config
        save_config(
            config = self._ledfx.config, 
            config_dir = self._ledfx.config_dir)

        response = { 'status' : 'success' }
        return web.json_response(data=response, status=200)

    async def post(self, request) -> web.Response:
        """Create a new integration, or update an existing one"""
        data = await request.json()

        integration_config = data.get("config")
        if integration_config is None:
            response = {
                "status": "failed",
                "reason": 'Required attribute "config" was not provided',
            }
            return web.json_response(data=response, status=500)

        integration_type = data.get("type")
        if integration_type is None:
            response = {
                "status": "failed",
                "reason": 'Required attribute "type" was not provided',
            }
            return web.json_response(data=response, status=500)

        integration_id = data.get("id")
        new = not bool(integration_id)
        if integration_id is None:
            # Create new integration if no id is given
            integration_id = generate_id(integration_config.get("name"))
            _LOGGER.info(
                ("Creating {} integration with config {}").format(
                    integration_type, integration_config
                )
            )
        else:
            # Update existing integration if valid id is given
            existing_integration = self._ledfx.integrations.get(integration_id)

            if existing_integration is None:
                response = {
                    "status": "failed",
                    "reason": f"Integration with id {integration_id} not found"
                }
                return web.json_response(data=response, status=500)

            _LOGGER.info(
                ("Updating {} integration '{}' with config {}").format(
                    integration_type, integration_id, integration_config
                )
            )

            self._ledfx.integrations.destroy(integration_id)

        integration = self._ledfx.integrations.create(
            id=integration_id,
            type=integration_type,
            config=integration_config,
            ledfx=self._ledfx
        )

        # Update and save the configuration
        if new:
            self._ledfx.config["integrations"].append(
                {
                    "id": integration.id,
                    "type": integration.type,
                    "config": integration.config,
                }
            )
        else:
            for integration in self._ledfx.config["integrations"]:
                if integration["id"] == integration_id:
                    integration["config"] = integration_config
                    break
                    # Update and save the configuration

        save_config(
            config=self._ledfx.config,
            config_dir=self._ledfx.config_dir,
        )

        response = {"status": "success"}
        return web.json_response(data=response, status=200)