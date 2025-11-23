"""Additional coverage tests for Onkyo Media Player."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME

from custom_components.onkyo.const import DOMAIN
from custom_components.onkyo.media_player import (
    OnkyoMediaPlayer,
    _detect_zones_safe,
    async_setup_entry,
)


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


@pytest.fixture
def mock_connection_manager():
    """Mock the connection manager."""
    manager = AsyncMock()
    manager.async_send_command = AsyncMock()
    manager.connected = True
    return manager


@pytest.fixture
def mock_receiver():
    """Mock the receiver."""
    receiver = MagicMock()
    receiver.register_callback = MagicMock()
    receiver.unregister_callback = MagicMock()
    return receiver


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    return MockConfigEntry(
        data={CONF_HOST: "1.2.3.4", CONF_NAME: "Onkyo Receiver", "max_volume": 100},
        options={"volume_resolution": 80},
        entry_id="test_entry_id",
    )


@pytest.mark.asyncio
async def test_detect_zones_safe_main_only(mock_connection_manager):
    """Test zone detection when only main zone is available."""
    mock_connection_manager.async_send_command.side_effect = Exception("Command failed")

    zones = await _detect_zones_safe(mock_connection_manager)

    assert zones == ["main"]
    # Should try to query zone2 and zone3
    assert mock_connection_manager.async_send_command.call_count == 2


@pytest.mark.asyncio
async def test_detect_zones_safe_all_zones(mock_connection_manager):
    """Test detection of all zones."""

    async def command_side_effect(type_, command):
        if command == "zone2.power=query":
            return "on"
        if command == "zone3.power=query":
            return "on"
        return None

    mock_connection_manager.async_send_command.side_effect = command_side_effect

    zones = await _detect_zones_safe(mock_connection_manager)

    assert "main" in zones
    assert "zone2" in zones
    assert "zone3" in zones


@pytest.mark.asyncio
async def test_async_setup_entry(
    hass, mock_config_entry, mock_connection_manager, mock_receiver
):
    """Test async_setup_entry with zone detection."""

    # Setup hass.data
    hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "receiver": mock_receiver,
            "connection_manager": mock_connection_manager,
            "name": "Onkyo Receiver",
        }
    }

    async_add_entities = MagicMock()

    with patch(
        "custom_components.onkyo.media_player._detect_zones_safe",
        return_value=["main", "zone2"],
    ) as mock_detect:
        await async_setup_entry(hass, mock_config_entry, async_add_entities)

        mock_detect.assert_awaited_once()
        assert async_add_entities.call_count == 1
        entities = async_add_entities.call_args[0][0]
        assert len(entities) == 2
        assert entities[0].name == "Onkyo Receiver main"
        assert entities[1].name == "Onkyo Receiver zone2"


@pytest.mark.asyncio
async def test_async_setup_entry_fail_safe(
    hass, mock_config_entry, mock_connection_manager, mock_receiver
):
    """Test async_setup_entry creates main zone even if detection fails."""

    hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "receiver": mock_receiver,
            "connection_manager": mock_connection_manager,
            "name": "Onkyo Receiver",
        }
    }

    async_add_entities = MagicMock()

    with patch(
        "custom_components.onkyo.media_player._detect_zones_safe",
        side_effect=Exception("Detection error"),
    ):
        await async_setup_entry(hass, mock_config_entry, async_add_entities)

        assert async_add_entities.call_count == 1
        entities = async_add_entities.call_args[0][0]
        assert len(entities) == 1
        assert entities[0].name == "Onkyo Receiver"
        assert entities[0]._zone == "main"


@pytest.mark.asyncio
async def test_async_setup_entry_no_zones_returned(
    hass, mock_config_entry, mock_connection_manager, mock_receiver
):
    """Test async_setup_entry when _detect_zones_safe returns empty list."""

    hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "receiver": mock_receiver,
            "connection_manager": mock_connection_manager,
            "name": "Onkyo Receiver",
        }
    }

    async_add_entities = MagicMock()

    with patch(
        "custom_components.onkyo.media_player._detect_zones_safe", return_value=[]
    ):
        await async_setup_entry(hass, mock_config_entry, async_add_entities)

        # Should fall back to creating main zone
        assert async_add_entities.call_count == 1
        entities = async_add_entities.call_args[0][0]
        assert len(entities) == 1
        assert entities[0]._zone == "main"


class TestOnkyoMediaPlayer:
    @pytest.fixture
    def player(self, hass, mock_config_entry, mock_connection_manager, mock_receiver):
        hass.async_create_task = MagicMock()
        player = OnkyoMediaPlayer(
            receiver=mock_receiver,
            connection_manager=mock_connection_manager,
            name="Onkyo Test",
            zone="main",
            hass=hass,
            entry=mock_config_entry,
        )
        # Manually set hass since we are not going through the full entity setup
        player.hass = hass
        player.async_write_ha_state = MagicMock()
        return player

    @pytest.mark.asyncio
    async def test_properties(self, player):
        """Test entity properties."""
        # Fix mock issue where host was missing in unique_id calculation test
        # In __init__, it uses entry.data.get("host", "unknown")
        # In MockConfigEntry above, host is in data.

        assert "1.2.3.4" in player.unique_id
        assert player.device_info is not None
        assert player.has_entity_name is True
        assert player.device_class == MediaPlayerDeviceClass.RECEIVER

        # Test available property
        player._attr_available = True
        player._conn_manager.connected = True
        assert player.available is True

        player._conn_manager.connected = False
        assert player.available is False

    @pytest.mark.asyncio
    async def test_async_added_to_hass(self, player):
        """Test async_added_to_hass."""
        player._async_update_all = AsyncMock()

        await player.async_added_to_hass()

        player._receiver.register_callback.assert_called_once()
        player._async_update_all.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_async_added_to_hass_fail(self, player):
        """Test async_added_to_hass handles update failure."""
        player._async_update_all = AsyncMock(side_effect=OSError("Connection failed"))

        await player.async_added_to_hass()

        player._receiver.register_callback.assert_called_once()
        player._async_update_all.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_receiver_update_power(self, player):
        """Test handling power update."""
        player._async_update_all = AsyncMock()

        # Power ON
        player._attr_state = MediaPlayerState.OFF
        player._handle_receiver_update("main", "power", "on")
        assert player.state == MediaPlayerState.ON

        # Check that async_create_task was called with a coroutine
        # Since hass.async_create_task is mocked, the coroutine passed to it
        # is never awaited so we can't use assert_awaited_once().
        # We check call_count instead.
        assert player._async_update_all.call_count == 1
        player.hass.async_create_task.assert_called_once()

        # Power OFF
        player._handle_receiver_update("main", "power", "standby")
        assert player.state == MediaPlayerState.OFF

    @pytest.mark.asyncio
    async def test_handle_receiver_update_volume(self, player):
        """Test handling volume update."""
        player._attr_volume_level = 0.0

        # Numeric volume
        # Resolution 80, Max 100.
        # 40 / (80 * 1.0) = 0.5
        player._handle_receiver_update("main", "volume", 40)
        assert player.volume_level == 0.5

        # Invalid volume
        player._handle_receiver_update("main", "volume", "invalid")
        assert player.volume_level == 0.5  # Unchanged

    @pytest.mark.asyncio
    async def test_handle_receiver_update_muting(self, player):
        """Test handling muting update."""
        player._handle_receiver_update("main", "muting", "on")
        assert player.is_volume_muted is True

        player._handle_receiver_update("main", "muting", "off")
        assert player.is_volume_muted is False

    @pytest.mark.asyncio
    async def test_handle_receiver_update_input(self, player):
        """Test handling input selector update."""
        # String
        player._handle_receiver_update("main", "input-selector", "dvd")
        assert player.source == "dvd"

        # Tuple
        player._handle_receiver_update("main", "selector", ("tv", "TV"))
        assert player.source == "tv"

    @pytest.mark.asyncio
    async def test_handle_receiver_update_wrong_zone(self, player):
        """Test handling update for wrong zone."""
        player._handle_receiver_update("zone2", "power", "on")
        # Should do nothing
        assert player.state == MediaPlayerState.OFF

    @pytest.mark.asyncio
    async def test_async_turn_off(self, player):
        """Test turning off."""
        await player.async_turn_off()
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "system-power=standby"
        )
        assert player.state == MediaPlayerState.OFF

    @pytest.mark.asyncio
    async def test_async_turn_off_fail(self, player):
        """Test turning off failure."""
        player._conn_manager.async_send_command.side_effect = OSError("Fail")
        with pytest.raises(OSError):
            await player.async_turn_off()

    @pytest.mark.asyncio
    async def test_async_turn_off_zone2(
        self, hass, mock_config_entry, mock_connection_manager, mock_receiver
    ):
        """Test turning off zone 2."""
        player = OnkyoMediaPlayer(
            receiver=mock_receiver,
            connection_manager=mock_connection_manager,
            name="Onkyo Test",
            zone="zone2",
            hass=hass,
            entry=mock_config_entry,
        )
        player.async_write_ha_state = MagicMock()

        await player.async_turn_off()
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "zone2.power=standby"
        )

    @pytest.mark.asyncio
    async def test_async_volume_ops(self, player):
        """Test volume operations."""
        # Set Volume
        # HA Volume 0.5 -> Receiver Volume: 0.5 * (100/100) * 80 = 40
        await player.async_set_volume_level(0.5)
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "master-volume=40"
        )
        assert player.volume_level == 0.5

        # Volume Up
        player._async_update_volume = AsyncMock()
        await player.async_volume_up()
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "master-volume=level-up"
        )
        player._async_update_volume.assert_awaited()

        # Volume Down
        await player.async_volume_down()
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "master-volume=level-down"
        )

    @pytest.mark.asyncio
    async def test_async_volume_ops_fail(self, player):
        """Test volume operations fail."""
        player._conn_manager.async_send_command.side_effect = OSError("Fail")
        with pytest.raises(OSError):
            await player.async_set_volume_level(0.5)
        with pytest.raises(OSError):
            await player.async_volume_up()
        with pytest.raises(OSError):
            await player.async_volume_down()

    @pytest.mark.asyncio
    async def test_async_mute_volume(self, player):
        """Test mute operations."""
        await player.async_mute_volume(True)
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "audio-muting=on"
        )
        assert player.is_volume_muted is True

        await player.async_mute_volume(False)
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "audio-muting=off"
        )
        assert player.is_volume_muted is False

    @pytest.mark.asyncio
    async def test_async_mute_volume_fail(self, player):
        """Test mute operations fail."""
        player._conn_manager.async_send_command.side_effect = OSError("Fail")
        with pytest.raises(OSError):
            await player.async_mute_volume(True)

    @pytest.mark.asyncio
    async def test_async_select_source(self, player):
        """Test selecting source."""
        await player.async_select_source("dvd")
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "input-selector=dvd"
        )
        assert player.source == "dvd"

    @pytest.mark.asyncio
    async def test_async_select_source_fail(self, player):
        """Test selecting source fail."""
        player._conn_manager.async_send_command.side_effect = OSError("Fail")
        with pytest.raises(OSError):
            await player.async_select_source("dvd")

    @pytest.mark.asyncio
    async def test_async_select_hdmi_output(self, player):
        """Test selecting HDMI output."""
        # Valid output
        await player.async_select_hdmi_output("out")
        player._conn_manager.async_send_command.assert_awaited_with(
            "command", "hdmi-output-selector=out"
        )

        # Invalid output
        with pytest.raises(ValueError):
            await player.async_select_hdmi_output("invalid_hdmi")

        # Wrong zone
        player._zone = "zone2"
        # Reset mock
        player._conn_manager.async_send_command.reset_mock()
        await player.async_select_hdmi_output("out")
        player._conn_manager.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_select_hdmi_output_fail(self, player):
        """Test selecting HDMI output fail."""
        player._conn_manager.async_send_command.side_effect = OSError("Fail")
        with pytest.raises(OSError):
            await player.async_select_hdmi_output("out")

    @pytest.mark.asyncio
    async def test_async_play_media_radio(self, player):
        """Test playing radio preset."""
        player._async_update_source = AsyncMock()

        # Mock source update to simulate switch to tuner
        player._attr_source = "tuner"

        await player.async_play_media("radio", "1")

        # Should select tuner first
        player._conn_manager.async_send_command.assert_any_await(
            "command", "input-selector=tuner"
        )
        # Then select preset
        player._conn_manager.async_send_command.assert_any_await("command", "preset=1")

    @pytest.mark.asyncio
    async def test_async_play_media_radio_wait_fail(self, player):
        """Test playing radio preset where tuner check timeout."""
        player._async_update_source = AsyncMock()

        # Mock source update to always return dvd
        player._attr_source = "dvd"

        await player.async_play_media("radio", "1")

        # Should still try to set preset even if timeout
        player._conn_manager.async_send_command.assert_any_await("command", "preset=1")

    @pytest.mark.asyncio
    async def test_async_play_media_fail(self, player):
        """Test playing media fail."""
        player._conn_manager.async_send_command.side_effect = OSError("Fail")
        with pytest.raises(OSError):
            await player.async_play_media("radio", "1")

    @pytest.mark.asyncio
    async def test_async_play_media_unsupported(self, player):
        """Test playing unsupported media."""
        await player.async_play_media("video", "1")
        player._conn_manager.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_source_list_success(self, player):
        """Test fetching source list successfully."""
        player._conn_manager.async_send_command.return_value = {
            "dvd": "DVD",
            "tv": "TV",
        }

        await player._async_fetch_source_list()

        assert "dvd" in player.source_list
        assert "tv" in player.source_list
        assert len(player.source_list) == 2

    @pytest.mark.asyncio
    async def test_fetch_source_list_failure(self, player):
        """Test fetching source list failure."""
        player._conn_manager.async_send_command.side_effect = OSError(
            "Connection error"
        )

        await player._async_fetch_source_list()

        assert player.source_list == []

    @pytest.mark.asyncio
    async def test_fetch_listening_modes_success(self, player):
        """Test fetching listening modes successfully."""
        player._conn_manager.async_send_command.return_value = {
            "stereo": "Stereo",
            "direct": "Direct",
        }

        await player._async_fetch_listening_modes()

        assert "stereo" in player._listening_modes
        assert "direct" in player._listening_modes

        attrs = player.extra_state_attributes
        assert "listening_modes" in attrs
        assert attrs["listening_modes"] == ["stereo", "direct"]

    @pytest.mark.asyncio
    async def test_fetch_listening_modes_failure(self, player):
        """Test fetching listening modes failure."""
        player._conn_manager.async_send_command.side_effect = OSError(
            "Connection error"
        )

        await player._async_fetch_listening_modes()

        assert player._listening_modes == []

    @pytest.mark.asyncio
    async def test_will_remove_from_hass(self, player):
        """Test cleanup."""
        await player.async_will_remove_from_hass()
        player._receiver.unregister_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_will_remove_from_hass_fail(self, player):
        """Test cleanup fail."""
        player._receiver.unregister_callback.side_effect = OSError("Fail")
        await player.async_will_remove_from_hass()
        # Should not raise

    @pytest.mark.asyncio
    async def test_volume_conversion_edges(self, player):
        """Test volume conversion edge cases."""
        # Test resolution=50, max=80
        # Create a new entry with desired options/data
        new_entry = MockConfigEntry(
            data={CONF_HOST: "1.2.3.4", CONF_NAME: "Onkyo Receiver", "max_volume": 80},
            options={"volume_resolution": 50},
            entry_id="test_entry_id_2",
        )
        player._entry = new_entry

        # 50 * (80/100) = 40 steps max

        # HA 1.0 -> Receiver 40
        assert player._ha_volume_to_receiver(1.0) == 40

        # Receiver 20 -> HA 0.5
        assert player._receiver_volume_to_ha(20) == 0.5

        # Test max_receiver_volume = 0 case (shouldn't happen but code handles it)
        zero_entry = MockConfigEntry(
            data={CONF_HOST: "1.2.3.4", CONF_NAME: "Onkyo Receiver", "max_volume": 0},
            options={"volume_resolution": 80},
            entry_id="test_entry_id_zero",
        )
        player._entry = zero_entry
        assert player._receiver_volume_to_ha(10) == 0.0
