"""Tests for the Onkyo media_player."""
import pytest
from unittest.mock import MagicMock, AsyncMock

from homeassistant.config_entries import ConfigEntry

from custom_components.onkyo.media_player import OnkyoMediaPlayer


class MockConfigEntry(ConfigEntry):
    """Mock config entry."""

    def __init__(self, *, data, options, entry_id="test-entry-id", **kwargs):
        """Initialize the mock config entry."""
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
async def test_update_volume_parses_tuple():
    """Test that async_update_volume correctly parses a tuple response."""
    # Setup
    receiver_mock = MagicMock()
    hass_mock = MagicMock()

    # A basic mock config entry
    mock_config_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver", "max_volume": 100},
        options={"volume_resolution": 100},
    )

    player = OnkyoMediaPlayer(
        receiver=receiver_mock,
        name="Test Player",
        zone="main",
        hass=hass_mock,
        entry=mock_config_entry,
    )

    # Mock the connection manager
    player._conn_manager = AsyncMock()

    # Mock the sequence of commands during an update
    async def command_side_effect(*args, **kwargs):
        command = args[1]
        if "power" in command:
            return ("system-power", "on")
        if "volume" in command:
            # The receiver can return a tuple
            return ("master-volume", 40)
        if "selector" in command:
            return "pc"
        if "muting" in command:
            return "off"
        return None

    player._conn_manager.async_send_command.side_effect = command_side_effect

    # Run the update
    await player.async_update()

    # Assert that the volume level is correctly parsed from the tuple
    # With resolution 100 and max_vol 100, receiver vol 40 should be HA vol 0.4
    assert player.volume_level == 0.4


@pytest.mark.asyncio
async def test_update_volume_does_not_crash_on_invalid_string():
    """Test that async_update_volume does not crash on a non-numeric string."""
    # Setup
    receiver_mock = MagicMock()
    hass_mock = MagicMock()

    # A basic mock config entry
    mock_config_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver", "max_volume": 100},
        options={"volume_resolution": 100},
    )

    player = OnkyoMediaPlayer(
        receiver=receiver_mock,
        name="Test Player",
        zone="main",
        hass=hass_mock,
        entry=mock_config_entry,
    )

    # Mock the connection manager
    player._conn_manager = AsyncMock()

    # Mock the sequence of commands during an update
    async def command_side_effect(*args, **kwargs):
        command = args[1]
        if "power" in command:
            return ("system-power", "on")
        if "volume" in command:
            # The receiver can return a non-numeric string
            return ("master-volume", "N/A")
        if "selector" in command:
            return "pc"
        if "muting" in command:
            return "off"
        return None

    player._conn_manager.async_send_command.side_effect = command_side_effect

    # Run the update - this should not raise an exception
    await player.async_update()

    # Assert that the volume level remains None as the value was invalid
    assert player.volume_level is None


@pytest.mark.asyncio
async def test_update_source_parses_tuple():
    """Test that async_update_source correctly parses a tuple response."""
    # Setup
    receiver_mock = MagicMock()
    hass_mock = MagicMock()
    mock_config_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver"},
        options={},
    )
    player = OnkyoMediaPlayer(
        receiver=receiver_mock,
        name="Test Player",
        zone="main",
        hass=hass_mock,
        entry=mock_config_entry,
    )
    player._conn_manager = AsyncMock()
    async def command_side_effect(*args, **kwargs):
        command = args[1]
        if "power" in command:
            return ("system-power", "on")
        if "volume" in command:
            return ("master-volume", 40)
        if "selector" in command:
            # When the source is changed, the receiver returns a tuple
            return ('input-selector', ('cbl-sat', 'CBL/SAT'))
        if "muting" in command:
            return "off"
        return None

    player._conn_manager.async_send_command.side_effect = command_side_effect
    await player.async_update()
    assert player.source == 'cbl-sat'


@pytest.mark.asyncio
async def test_update_source_handles_empty_tuple():
    """Test that async_update_source does not crash on an empty tuple response."""
    # Setup
    receiver_mock = MagicMock()
    hass_mock = MagicMock()
    mock_config_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver"},
        options={},
    )
    player = OnkyoMediaPlayer(
        receiver=receiver_mock,
        name="Test Player",
        zone="main",
        hass=hass_mock,
        entry=mock_config_entry,
    )
    player._conn_manager = AsyncMock()

    # Mock the command to return an empty tuple for the source
    async def command_side_effect(*args, **kwargs):
        command = args[1]
        if "power" in command:
            return ("system-power", "on")
        if "volume" in command:
            return ("master-volume", 40)
        if "selector" in command:
            # This is the problematic response
            return ('input-selector', ())
        if "muting" in command:
            return "off"
        return None

    player._conn_manager.async_send_command.side_effect = command_side_effect

    # This call should not raise an IndexError
    await player.async_update()

    # The source should remain at its initial state (None) because the response was invalid
    assert player.source is None
