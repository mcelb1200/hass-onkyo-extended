import pytest
from unittest.mock import MagicMock
from custom_components.onkyo.media_player import OnkyoMediaPlayer


# Minimal mock for ConfigEntry
class MockConfigEntry:
    def __init__(self, data, options=None):
        self._data = data
        self._options = options if options is not None else {}

    @property
    def data(self):
        return self._data

    @property
    def options(self):
        return self._options


# Test cases for volume conversion
@pytest.mark.parametrize(
    "receiver_volume, max_volume, resolution, expected_ha_volume",
    [
        # Scenario 1: No max volume limit (max_volume is 100)
        (0, 100, 80, 0.0),  # Min volume
        (40, 100, 80, 0.5),  # Mid volume
        (80, 100, 80, 1.0),  # Max volume
        # Scenario 2: With max volume limit (e.g., 80), max receiver volume is 64
        (0, 80, 80, 0.0),  # Min volume
        (32, 80, 80, 0.5),  # Mid volume (half of the usable range)
        (51, 80, 80, 0.796875),  # Corresponds to HA volume 0.8
        (64, 80, 80, 1.0),  # Max volume (full slider)
        # Scenario 3: Different resolution (e.g., 100)
        (50, 100, 100, 0.5),  # Mid volume
        (100, 100, 100, 1.0),  # Max volume
        (50, 80, 100, 0.625),  # 50 is 62.5% of 80
    ],
)
# pylint: disable=all
def test_receiver_volume_to_ha(
    receiver_volume, max_volume, resolution, expected_ha_volume
):
    # Mock necessary dependencies
    mock_receiver = MagicMock()
    mock_hass = MagicMock()
    mock_conn_manager = MagicMock()

    # Create mock config entry with volume settings
    mock_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver"},
        options={"max_volume": max_volume, "volume_resolution": resolution},
    )

    # Instantiate the media player
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_conn_manager,
        name="Test Receiver",
        zone="main",
        hass=mock_hass,
        entry=mock_entry,
    )

    # Perform the conversion
    ha_volume = player._receiver_volume_to_ha(receiver_volume)

    # Assert the result is as expected, allowing for small float inaccuracies
    assert ha_volume == pytest.approx(expected_ha_volume, abs=1e-3)


def test_receiver_volume_to_ha_zero_max_volume():
    """Test volume conversion with max_volume set to 0 to prevent division by zero."""
    # pylint: disable=all
    mock_receiver = MagicMock()
    mock_hass = MagicMock()
    mock_conn_manager = MagicMock()
    mock_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver"},
        options={"max_volume": 0, "volume_resolution": 80},
    )
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_conn_manager,
        name="Test Receiver",
        zone="main",
        hass=mock_hass,
        entry=mock_entry,
    )

    # This should not raise an error
    ha_volume = player._receiver_volume_to_ha(0)
    assert ha_volume == 0.0


@pytest.mark.parametrize(
    "ha_volume, max_volume, resolution, expected_receiver_volume",
    [
        (0.5, 100, 80, 40),  # Mid volume
        (0.499, 100, 80, 40),  # Value that should be rounded up
        (0.493, 100, 80, 39),  # Value that should be rounded down
    ],
)
# pylint: disable=all
def test_ha_volume_to_receiver(
    ha_volume, max_volume, resolution, expected_receiver_volume
):
    """Test conversion from HA volume to receiver volume scale."""

    # Mock necessary dependencies
    mock_receiver = MagicMock()
    mock_hass = MagicMock()
    mock_conn_manager = MagicMock()

    # Create mock config entry with volume settings
    mock_entry = MockConfigEntry(
        data={"host": "1.2.3.4", "name": "Test Receiver"},
        options={"max_volume": max_volume, "volume_resolution": resolution},
    )

    # Instantiate the media player
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_conn_manager,
        name="Test Receiver",
        zone="main",
        hass=mock_hass,
        entry=mock_entry,
    )

    # Perform the conversion
    receiver_volume = player._ha_volume_to_receiver(ha_volume)

    # Assert the result is as expected
    assert receiver_volume == expected_receiver_volume
