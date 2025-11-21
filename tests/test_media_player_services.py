import pytest
from unittest.mock import MagicMock, AsyncMock
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
async def test_select_hdmi_output_validation():
    """Test validation for select_hdmi_output service."""
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

    # Test valid output
    await player.async_select_hdmi_output("out")
    conn_manager_mock.async_send_command.assert_awaited_with(
        "command", "hdmi-output-selector=out"
    )

    # Test invalid output
    with pytest.raises(ValueError, match="Invalid HDMI output"):
        await player.async_select_hdmi_output("invalid_option")
