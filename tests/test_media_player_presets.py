from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.onkyo.media_player import OnkyoMediaPlayer


class MockConfigEntry(ConfigEntry):
    """Mock config entry."""

    def __init__(self, *, data, options, entry_id="test-entry-id", **kwargs):
        super().__init__(
            entry_id=entry_id,
            data=data,
            options=options,
            domain=kwargs.get("domain", "onkyo"),
            title=kwargs.get("title", "Onkyo"),
            source=kwargs.get("source", "user"),
            unique_id=kwargs.get("unique_id", "12345"),
            version=kwargs.get("version", 1),
            minor_version=kwargs.get("minor_version", 1),
            discovery_keys={},
        )


@pytest.mark.asyncio
async def test_play_media_radio_presets():
    """Test playing radio presets with correct source selection."""
    receiver_mock = MagicMock()
    hass_mock = MagicMock()
    conn_manager_mock = AsyncMock()

    mock_config_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver"},
        options={},
    )
    player = OnkyoMediaPlayer(
        receiver=receiver_mock,
        connection_manager=conn_manager_mock,
        name="Test Player",
        zone="main",
        hass=hass_mock,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    # Mock async_select_source to verify it receives "tuner"
    player.async_select_source = AsyncMock()

    # Mock update source to simulate switching
    player._async_update_source = AsyncMock()

    # Mock internal state change
    async def update_source_side_effect():
        player._attr_source = "Tuner"

    player._async_update_source.side_effect = update_source_side_effect

    await player.async_play_media("radio", "1")

    # Verify "tuner" was selected, not "radio"
    player.async_select_source.assert_awaited_with("tuner")

    # Verify preset command was sent
    conn_manager_mock.async_send_command.assert_awaited_with("command", "preset=1")
