from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.media_player import MediaPlayerState
from homeassistant.core import HomeAssistant

from custom_components.onkyo.media_player import OnkyoMediaPlayer


@pytest.mark.asyncio
async def test_async_turn_on_delay(hass: HomeAssistant):
    """Test that async_turn_on waits 1.5s before polling."""
    receiver = MagicMock()
    connection_manager = MagicMock()
    # Mock async_send_command to return an awaitable
    connection_manager.async_send_command = AsyncMock(return_value="on")

    entry = MagicMock()
    entry.data = {"host": "1.2.3.4", "name": "Test Receiver"}
    entry.options = {}

    player = OnkyoMediaPlayer(
        receiver, connection_manager, "Test Receiver", "main", hass, entry
    )
    # Manually set hass since __init__ doesn't set it
    player.hass = hass
    player.async_write_ha_state = MagicMock()

    # Mock asyncio.sleep
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        # Mock _async_get_power_state to return 'on' immediately
        with patch.object(
            player, "_async_get_power_state", return_value="on"
        ):
            await player.async_turn_on()

            # Verify sleep was called with 1.5
            mock_sleep.assert_any_call(1.5)

            # Verify command sent
            connection_manager.async_send_command.assert_any_call(
                "command", "system-power=on"
            )


@pytest.mark.asyncio
async def test_handle_receiver_update_triggers_update(hass: HomeAssistant):
    """Test that _handle_receiver_update triggers update when power turns on."""
    receiver = MagicMock()
    connection_manager = MagicMock()

    entry = MagicMock()
    entry.data = {"host": "1.2.3.4", "name": "Test Receiver"}
    entry.options = {}

    player = OnkyoMediaPlayer(
        receiver, connection_manager, "Test Receiver", "main", hass, entry
    )
    # Manually set hass since __init__ doesn't set it
    player.hass = hass
    player.async_write_ha_state = MagicMock()
    player._async_update_all = MagicMock()

    # Mock hass.async_create_task
    hass.async_create_task = MagicMock()

    # Initial state is OFF
    player._attr_state = MediaPlayerState.OFF

    # Simulate power ON update
    player._handle_receiver_update("main", "power", "on")

    # Verify state changed
    assert player.state == MediaPlayerState.ON

    # Verify update task created
    # hass.async_create_task is called to schedule the coroutine
    hass.async_create_task.assert_called()

    # Simulate another update (e.g. volume) while ON
    hass.async_create_task.reset_mock()
    # Pass integer volume
    player._handle_receiver_update("main", "volume", 10)

    # Verify no update task created (since power didn't change from OFF to ON)
    hass.async_create_task.assert_not_called()


@pytest.mark.asyncio
async def test_handle_receiver_update_volume_robustness(hass: HomeAssistant):
    """Test that _handle_receiver_update handles non-numeric volume gracefully."""
    receiver = MagicMock()
    connection_manager = MagicMock()

    entry = MagicMock()
    entry.data = {"host": "1.2.3.4", "name": "Test Receiver"}
    entry.options = {}

    player = OnkyoMediaPlayer(
        receiver, connection_manager, "Test Receiver", "main", hass, entry
    )
    player.hass = hass
    player.async_write_ha_state = MagicMock()

    # Simulate non-numeric volume update (should not crash)
    try:
        player._handle_receiver_update("main", "volume", "N/A")
    except Exception as e:
        pytest.fail(f"Should not have raised exception: {e}")
