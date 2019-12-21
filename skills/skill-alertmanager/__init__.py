from aiohttp.web import Request

from opsdroid.skill import Skill
from opsdroid.matchers import match_webhook
from opsdroid.events import Message

import json
import logging
import os
import pprint

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOG_LEVEL)
_LOGGER = logging.getLogger(__name__)


class AlertManager(Skill):
    @match_webhook('webhook')
    async def alertmanager(self, opsdroid, config, message):
        if type(message) is Message or type(message) is not Request:
            return

        payload = await message.json()
        _LOGGER.debug('payload received by alertmanager: ' +
                      pprint.pformat(payload))

        message = Message(None,
                          config.get("room",
                                     opsdroid.default_connector.default_room),
                          opsdroid.default_connector,
                          "")

        for alert in payload["alerts"]:
            msg = ""
            if "message" in alert["annotations"]:
                msg = alert["annotations"]["message"]
            elif "description" in alert["annotations"]:
                msg = alert["annotations"]["description"]
            await message.respond(
                "{status} {name} ({severity}): {message}".format(
                    status=alert["status"].upper(),
                    name=alert["labels"]["alertname"],
                    severity=alert["labels"]["severity"].upper(),
                    message=msg)
            )
