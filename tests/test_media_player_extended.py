"""Extended tests for the Onkyo media_player."""

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from homeassistant.components.media_player import (
    MediaPlayerState,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.onkyo.const import ATTR_HDMI_OUTPUT, DOMAIN
from custom_components.onkyo.media_player import (
    OnkyoMediaPlayer,
    _detect_zones_safe,
    async_setup_entry,
)


@pytest.fixture
def mock_connection_manager():
    """Mock the connection manager."""
    manager = AsyncMock()
    manager.connected = True
    return manager


@pytest.fixture
def mock_receiver():
    """Mock the receiver."""
    return MagicMock()


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            "host": "1.2.3.4",
            "name": "Onkyo Receiver",
            "max_volume": 100,
        },
        options={
            "volume_resolution": 80,
        },
        entry_id="test_entry_id",
    )


@pytest.mark.asyncio
async def test_setup_entry_successful(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test successful setup of entry with zone detection."""
    hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "receiver": mock_receiver,
            "connection_manager": mock_connection_manager,
            "name": "Onkyo Receiver",
        }
    }

    # Mock zone detection to return main and zone2
    mock_connection_manager.async_send_command.side_effect = [
        "on",  # zone2.power=query
        None,  # zone3.power=query (timeout/fail)
    ]

    async_add_entities = MagicMock()

    with patch(
        "custom_components.onkyo.media_player._detect_zones_safe",
        return_value=["main", "zone2"],
    ):
        await async_setup_entry(hass, mock_config_entry, async_add_entities)

    assert async_add_entities.called
    entities = async_add_entities.call_args[0][0]
    assert len(entities) == 2
    assert entities[0].name == "Onkyo Receiver main"
    assert entities[1].name == "Onkyo Receiver zone2"


@pytest.mark.asyncio
async def test_setup_entry_detection_fails_creates_main(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test setup creates main zone if detection fails."""
    hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "receiver": mock_receiver,
            "connection_manager": mock_connection_manager,
            "name": "Onkyo Receiver",
        }
    }

    async_add_entities = MagicMock()

    # Mock detection raising exception
    with patch(
        "custom_components.onkyo.media_player._detect_zones_safe",
        side_effect=Exception("Detection failed"),
    ):
        await async_setup_entry(hass, mock_config_entry, async_add_entities)

    assert async_add_entities.called
    entities = async_add_entities.call_args[0][0]
    assert len(entities) == 1
    assert entities[0].name == "Onkyo Receiver"
    assert entities[0]._zone == "main"


@pytest.mark.asyncio
async def test_detect_zones_safe(mock_connection_manager):
    """Test safe zone detection."""
    # Test finding all zones
    mock_connection_manager.async_send_command.side_effect = [
        "on",
        "on",
    ]  # zone2, zone3
    zones = await _detect_zones_safe(mock_connection_manager)
    assert "main" in zones
    assert "zone2" in zones
    assert "zone3" in zones

    # Test finding only main (others fail)
    mock_connection_manager.async_send_command.side_effect = [
        Exception("Timeout"),
        Exception("Timeout"),
    ]
    zones = await _detect_zones_safe(mock_connection_manager)
    assert zones == ["main"]

    # Test connection manager failure
    mock_connection_manager.async_send_command.side_effect = Exception(
        "General Failure"
    )
    zones = await _detect_zones_safe(mock_connection_manager)
    assert zones == ["main"]  # Should always return at least main


@pytest.mark.asyncio
async def test_turn_off(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test turn off."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    await player.async_turn_off()

    mock_connection_manager.async_send_command.assert_called_with(
        "command", "system-power=standby"
    )
    assert player.state == MediaPlayerState.OFF


@pytest.mark.asyncio
async def test_volume_operations(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test volume set, up, and down."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    # Test set volume
    # Max vol 100, resolution 80. HA 0.5 -> 0.5 * (100/100) * 80 = 40
    await player.async_set_volume_level(0.5)
    mock_connection_manager.async_send_command.assert_called_with(
        "command", "master-volume=40"
    )
    assert player.volume_level == 0.5

    # Reset mock for volume up test
    mock_connection_manager.async_send_command.reset_mock()

    # Test volume up
    # async_volume_up calls command="master-volume=level-up"
    # then sleeps then calls update command="master-volume=query"
    # We need to mock the sequence of calls if we want to verify all of them,
    # or just check the first one

    # Mocking side effect to avoid errors if any return value is expected
    mock_connection_manager.async_send_command.return_value = None

    with patch("asyncio.sleep", new_callable=AsyncMock):
        await player.async_volume_up()

    # Check that level-up was sent
    assert (
        call("command", "master-volume=level-up")
        in mock_connection_manager.async_send_command.call_args_list
    )

    # Reset mock for volume down test
    mock_connection_manager.async_send_command.reset_mock()

    # Test volume down
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await player.async_volume_down()

    assert (
        call("command", "master-volume=level-down")
        in mock_connection_manager.async_send_command.call_args_list
    )


@pytest.mark.asyncio
async def test_mute_volume(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test mute and unmute."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    # Mute
    await player.async_mute_volume(True)
    mock_connection_manager.async_send_command.assert_called_with(
        "command", "audio-muting=on"
    )
    assert player.is_volume_muted is True

    # Unmute
    await player.async_mute_volume(False)
    mock_connection_manager.async_send_command.assert_called_with(
        "command", "audio-muting=off"
    )
    assert player.is_volume_muted is False


@pytest.mark.asyncio
async def test_select_source(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test source selection."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    await player.async_select_source("video1")
    mock_connection_manager.async_send_command.assert_called_with(
        "command", "input-selector=video1"
    )
    assert player.source == "video1"


@pytest.mark.asyncio
async def test_play_media_radio(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test play media with radio preset."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    # Mock update source to confirm tuner selection
    player._async_update_source = AsyncMock()
    # Need to simulate source becoming tuner
    player._attr_source = "tuner"

    await player.async_play_media("radio", "1")

    # Verify it switched to tuner first
    mock_connection_manager.async_send_command.assert_any_call(
        "command", "input-selector=tuner"
    )
    # Then selected preset
    mock_connection_manager.async_send_command.assert_called_with("command", "preset=1")


@pytest.mark.asyncio
async def test_play_media_unsupported(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test play media with unsupported type."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    await player.async_play_media("music", "some_song")
    # Should check warning log, but for now ensure no command sent for preset

    # We can verify no calls if we reset mock
    mock_connection_manager.async_send_command.reset_mock()
    await player.async_play_media("video", "1")
    mock_connection_manager.async_send_command.assert_not_called()


@pytest.mark.asyncio
async def test_select_hdmi_output(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test HDMI output selection."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    # Valid output
    await player.async_select_hdmi_output("out")
    mock_connection_manager.async_send_command.assert_called_with(
        "command", "hdmi-output-selector=out"
    )
    assert player.extra_state_attributes[ATTR_HDMI_OUTPUT] == "out"

    # Invalid output
    with pytest.raises(ValueError):
        await player.async_select_hdmi_output("invalid_output")

    # Not main zone
    player_zone2 = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player Z2",
        zone="zone2",
        hass=hass,
        entry=mock_config_entry,
    )
    mock_connection_manager.async_send_command.reset_mock()
    await player_zone2.async_select_hdmi_output("out")
    mock_connection_manager.async_send_command.assert_not_called()


@pytest.mark.asyncio
async def test_handle_receiver_update(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test handling of receiver updates."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.hass = (
        hass  # Manual assignment needed for async_create_task in isolation tests
    )

    player.async_write_ha_state = MagicMock()
    player._async_update_all = AsyncMock()

    # Power update
    player._handle_receiver_update("main", "power", "on")
    assert player.state == MediaPlayerState.ON
    assert player.available is True
    # Should trigger update all on transition from OFF to ON
    # But initial state is OFF.
    player._async_update_all.assert_called_once()

    player._async_update_all.reset_mock()

    # Power off
    player._handle_receiver_update("main", "power", "standby")
    assert player.state == MediaPlayerState.OFF

    # Volume update
    player._handle_receiver_update("main", "volume", 40)
    # 40 / 80 = 0.5
    assert player.volume_level == 0.5

    # Muting update
    player._handle_receiver_update("main", "muting", "on")
    assert player.is_volume_muted is True

    # Source update (simple)
    player._handle_receiver_update("main", "input-selector", "video1")
    assert player.source == "video1"

    # Source update (tuple)
    player._handle_receiver_update("main", "input-selector", ("video2", "Video 2"))
    assert player.source == "video2"

    # Wrong zone update
    player._handle_receiver_update("zone2", "power", "on")
    # State shouldn't change from OFF (set above)
    assert player.state == MediaPlayerState.OFF


@pytest.mark.asyncio
async def test_async_update_all(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test async_update_all with full data fetch."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    # Mock responses for all update calls
    async def command_side_effect(*args, **kwargs):
        command = args[1]
        if "system-power=query" in command:
            return ("system-power", "on")
        if "master-volume=query" in command:
            return ("master-volume", 20)
        if "input-selector=query" in command:
            return ("input-selector", ("dvd", "DVD"))
        if "audio-muting=query" in command:
            return "off"
        if command == "SLIQSTN":
            return {"dvd": "DVD", "video1": "Video 1"}
        if command == "LMQSTN":
            return {"stereo": "Stereo", "direct": "Direct"}
        return None

    mock_connection_manager.async_send_command.side_effect = command_side_effect

    await player._async_update_all()

    assert player.state == MediaPlayerState.ON
    assert player.volume_level == 0.25  # 20/80
    assert player.source == "dvd"
    assert player.is_volume_muted is False
    assert "dvd" in player.source_list
    assert "stereo" in player.extra_state_attributes["listening_modes"]


@pytest.mark.asyncio
async def test_remove_from_hass(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test cleanup when removed."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    await player.async_will_remove_from_hass()
    mock_receiver.unregister_callback.assert_called_with(player._handle_receiver_update)


@pytest.mark.asyncio
async def test_update_all_oserror(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test _async_update_all with OSError."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    player._async_get_power_state = AsyncMock(side_effect=OSError("Connection failed"))

    await player.async_update()

    assert player.available is False


@pytest.mark.asyncio
async def test_turn_on_timeout(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test turn on with timeout waiting for power state."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )
    player.async_write_ha_state = MagicMock()

    # Mock always returning standby
    player._async_get_power_state = AsyncMock(return_value="standby")
    player._async_fetch_source_list = AsyncMock()

    with patch("asyncio.sleep", new_callable=AsyncMock):
        await player.async_turn_on()

    # Should be optimistically ON
    assert player.state == MediaPlayerState.ON
    assert player.available is True


@pytest.mark.asyncio
async def test_turn_off_failure(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test turn off failure."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    with pytest.raises(OSError):
        await player.async_turn_off()


@pytest.mark.asyncio
async def test_set_volume_failure(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test set volume failure."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    with pytest.raises(OSError):
        await player.async_set_volume_level(0.5)


@pytest.mark.asyncio
async def test_volume_up_failure(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test volume up failure."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    with pytest.raises(OSError):
        await player.async_volume_up()


@pytest.mark.asyncio
async def test_volume_down_failure(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test volume down failure."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    with pytest.raises(OSError):
        await player.async_volume_down()


@pytest.mark.asyncio
async def test_mute_failure(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test mute failure."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    with pytest.raises(OSError):
        await player.async_mute_volume(True)


@pytest.mark.asyncio
async def test_select_source_failure(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test select source failure."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    with pytest.raises(OSError):
        await player.async_select_source("dvd")


@pytest.mark.asyncio
async def test_play_media_failure(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test play media failure."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    with pytest.raises(OSError):
        await player.async_play_media("radio", "1")


@pytest.mark.asyncio
async def test_get_power_state_oserror(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test _async_get_power_state OSError handling."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    state = await player._async_get_power_state()
    assert state == "unknown"


@pytest.mark.asyncio
async def test_update_volume_oserror(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test _async_update_volume OSError handling."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    # Should not raise
    await player._async_update_volume()


@pytest.mark.asyncio
async def test_update_source_oserror(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test _async_update_source OSError handling."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    # Should not raise
    await player._async_update_source()


@pytest.mark.asyncio
async def test_update_mute_oserror(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test _async_update_mute OSError handling."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    # Should not raise
    await player._async_update_mute()


@pytest.mark.asyncio
async def test_fetch_lists_failure(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test fetching lists failure."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.side_effect = OSError("Failed")

    await player._async_fetch_source_list()
    assert player.source_list == []

    await player._async_fetch_listening_modes()
    assert player.extra_state_attributes.get("listening_modes") is None


@pytest.mark.asyncio
async def test_fetch_lists_empty(
    hass, mock_connection_manager, mock_receiver, mock_config_entry
):
    """Test fetching lists returns empty or None."""
    player = OnkyoMediaPlayer(
        receiver=mock_receiver,
        connection_manager=mock_connection_manager,
        name="Test Player",
        zone="main",
        hass=hass,
        entry=mock_config_entry,
    )

    mock_connection_manager.async_send_command.return_value = None

    await player._async_fetch_source_list()
    assert player.source_list == []

    await player._async_fetch_listening_modes()
    assert player.extra_state_attributes.get("listening_modes") is None
