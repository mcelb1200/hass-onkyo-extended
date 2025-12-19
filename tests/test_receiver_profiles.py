"""Test receiver profiles integration."""
import pytest
from unittest.mock import patch, MagicMock
from homeassistant.const import CONF_HOST, CONF_NAME
from custom_components.onkyo.const import (
    DOMAIN,
    CONF_MAX_VOLUME,
    CONF_RECEIVER_MAX_VOLUME,
    CONF_SOURCES,
    CONF_VOLUME_RESOLUTION,
)
from custom_components.onkyo.config_flow import OnkyoConfigFlow
from custom_components.onkyo.receiver_profiles import RECEIVER_PROFILES

@pytest.mark.asyncio
async def test_config_flow_defaults_from_profile(hass):
    """Test that config flow picks up defaults from profile."""

    # Mock eISCP to return a specific model name
    with patch("custom_components.onkyo.config_flow.eISCP") as mock_eiscp, \
         patch("custom_components.onkyo.config_flow.build_sources_list") as mock_build_sources:

        mock_receiver = MagicMock()
        mock_receiver.model_name = "VSX-831"
        mock_eiscp.return_value = mock_receiver

        # Setup source list mock
        mock_build_sources.return_value = {"bd": "Blu-ray", "tv": "TV"}

        flow = OnkyoConfigFlow()
        flow.hass = hass
        # Need to initialize context usually handled by data entry flow
        flow.context = {}

        result = await flow.async_step_user({
            CONF_HOST: "192.168.1.100",
            CONF_NAME: "My Pioneer",
            CONF_RECEIVER_MAX_VOLUME: 100,
        })

        assert result["type"] == "create_entry"
        options = result["options"]

        # Check defaults from VSX-831 profile
        assert options[CONF_MAX_VOLUME] == 55
        # volume_resolution is None in profile, so it defaults to 80
        assert options[CONF_VOLUME_RESOLUTION] == 80

        # Verify sources are set correctly
        assert options[CONF_SOURCES] == {"bd": "Blu-ray", "tv": "TV"}

@pytest.mark.asyncio
async def test_helpers_build_sources_list_from_profile():
    """Test build_sources_list uses profile sources."""
    from custom_components.onkyo.helpers import build_sources_list

    # "VSX-LX101" has specific sources in profile
    sources = build_sources_list("VSX-LX101")

    # Check some known sources from profile
    assert sources["bd"] == "Blu-ray"
    assert sources["tv"] == "TV (ARC)"

    # Ensure profile filtering works (video1 is not in the profile)
    assert "video1" not in sources

    # Test fallback
    sources_fallback = build_sources_list("UnknownModel")
    assert sources_fallback != sources
    # Should contain standard sources
    assert "video1" in sources_fallback or "game" in sources_fallback
