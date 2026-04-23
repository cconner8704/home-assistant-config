"""LG TV Picture Settings service.

Exposes the service `lg_picture.set_settings` which uses aiopylgtv's
luna_request trick (createAlert -> closeAlert with onclose handler) to
apply picture settings on a paired LG webOS TV.

pictureMode itself is patched on webOS 6+, but backlight/brightness/
contrast/color adjustments still apply. Bedtime dimming use case.
"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from aiopylgtv import WebOsClient

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "lg_picture"
SERVICE_SET_SETTINGS = "set_settings"

_SETTING_KEYS = ("backlight", "brightness", "contrast", "color")

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("host"): vol.All(str, vol.Length(min=1)),
        vol.Required("client_key"): vol.All(str, vol.Length(min=1)),
        vol.Optional("backlight"): vol.Coerce(str),
        vol.Optional("brightness"): vol.Coerce(str),
        vol.Optional("contrast"): vol.Coerce(str),
        vol.Optional("color"): vol.Coerce(str),
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async def handle_set(call: ServiceCall) -> None:
        host: str = call.data["host"]
        key: str = call.data["client_key"]
        settings: dict[str, Any] = {
            k: call.data[k] for k in _SETTING_KEYS if k in call.data
        }
        if not settings:
            _LOGGER.warning("lg_picture.set_settings called with no settings")
            return

        client = await WebOsClient.create(host, client_key=key)
        try:
            await client.connect()
            await client.set_current_picture_settings(settings)
            _LOGGER.info("Applied picture settings to %s: %s", host, settings)
        finally:
            await client.disconnect()

    hass.services.async_register(
        DOMAIN, SERVICE_SET_SETTINGS, handle_set, schema=SERVICE_SCHEMA
    )
    return True
