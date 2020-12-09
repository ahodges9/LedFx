from ledfx.api import RestEndpoint
from aiohttp import web
import logging

_LOGGER = logging.getLogger(__name__)


class EffectEndpoint(RestEndpoint):

    ENDPOINT_PATH = "/api/effects/{effect_id}"

    async def get(self, effect_id) -> web.Response:
        effect = self._ledfx.effects.get_class(effect_id)
        if effect is None:
            response = {"not found": 404}
            return web.json_response(data=response, status=404)

        response = {"schema": str(effect.schema())}
        return web.json_response(data=response, status=200)
