"""Test for source parsing bug."""

from unittest.mock import AsyncMock, MagicMock

import pytest
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
            discovery_keys={},
        )


@pytest.mark.asyncio
async def test_update_source_wrong_command_tuple():
    """Test that async_update_source parses ('command', 'value') correctly."""
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

    async def command_side_effect(*args, **kwargs):
        command = args[1]
        if "selector" in command:
            # Bug reproduction: tuple is (command, value)
            return ("input-selector", "video2")
        return None

    player._conn_manager.async_send_command.side_effect = command_side_effect
    await player._async_update_source()

    # We expect 'video2', but the bug will likely produce 'input-selector'
    assert player.source == "video2"
