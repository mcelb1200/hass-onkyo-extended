"""Tests for the Onkyo media_player volume conversion."""
import pytest
from unittest.mock import MagicMock, AsyncMock

from homeassistant.config_entries import ConfigEntry

from custom_components.onkyo.media_player import OnkyoMediaPlayer


class MockConfigEntry(ConfigEntry):
    """Mock config entry."""

    def __init__(self, *, data, options, entry_id="test-entry-id", **kwargs):
        """Initialize the mock config entry."""
        # Add all required fields for a ConfigEntry
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
            discovery_keys=kwargs.get("discovery_keys", {}),
        )


@pytest.mark.asyncio
async def test_update_volume_does_not_crash_on_invalid_string():
    """Test that async_update_volume handles non-integer string from receiver."""
    # Setup
    receiver_mock = MagicMock()
    hass_mock = MagicMock()

    # A basic mock config entry
    mock_config_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver"},
        options={},
        domain="onkyo",
        title="Onkyo",
    )

    player = OnkyoMediaPlayer(
        receiver=receiver_mock,
        name="Test Player",
        zone="main",
        hass=hass_mock,
        entry=mock_config_entry,
    )

    # Mock the connection manager to return an invalid volume string
    player._conn_manager = AsyncMock()

    # Mock the sequence of commands during an update
    async def command_side_effect(*args, **kwargs):
        command = args[1]
        if "power" in command:
            return ("system-power", "on")
        if "volume" in command:
            # This is the problematic value
            return "N/A"
        if "selector" in command:
            return "pc"
        if "muting" in command:
            return "off"
        return None

    player._conn_manager.async_send_command.side_effect = command_side_effect

    # This call should not raise an exception.
    await player.async_update()

    # Assert that the volume level is unchanged (it's None by default)
    assert player.volume_level is None
