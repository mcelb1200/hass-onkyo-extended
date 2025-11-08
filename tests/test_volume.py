"""Tests for volume conversion in the Onkyo media_player."""
import pytest
from unittest.mock import MagicMock

from custom_components.onkyo.media_player import OnkyoMediaPlayer
from homeassistant.config_entries import ConfigEntry


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

def test_volume_conversion_handles_zero_max_volume():
    """Test that _receiver_volume_to_ha handles a max_volume of 0."""
    # Setup
    receiver_mock = MagicMock()
    hass_mock = MagicMock()

    # Config entry with max_volume set to 0
    mock_config_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver", "max_volume": 0},
        options={"volume_resolution": 100},
    )

    player = OnkyoMediaPlayer(
        receiver=receiver_mock,
        name="Test Player",
        zone="main",
        hass=hass_mock,
        entry=mock_config_entry,
    )

    # Call the function directly and assert it doesn't raise an exception
    ha_volume = player._receiver_volume_to_ha(50)
    assert ha_volume == 0.0
