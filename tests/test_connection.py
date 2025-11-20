"""Tests for the Onkyo connection manager."""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from custom_components.onkyo.connection import OnkyoConnectionManager

@pytest.fixture
def mock_receiver():
    receiver = MagicMock()
    receiver.command = MagicMock()
    receiver.disconnect = MagicMock()
    return receiver

@pytest.fixture
def connection_manager(hass, mock_receiver):
    return OnkyoConnectionManager(hass, mock_receiver)

@pytest.mark.asyncio
async def test_send_command_success(hass, connection_manager, mock_receiver):
    """Test sending a command successfully."""
    mock_receiver.command.return_value = "success"

    # Simulate successful connection
    connection_manager._is_connected = True

    result = await connection_manager.async_send_command("test-command")

    assert result == "success"
    assert mock_receiver.command.called

@pytest.mark.asyncio
async def test_send_command_reconnect_success(hass, connection_manager, mock_receiver):
    """Test reconnection logic when not connected."""
    connection_manager._is_connected = False
    mock_receiver.command.return_value = "success"

    result = await connection_manager.async_send_command("test-command")

    assert result == "success"
    assert connection_manager.connected
    # Should have called command twice: once for reconnect check, once for actual command
    assert mock_receiver.command.call_count >= 2

@pytest.mark.asyncio
async def test_send_command_failure(hass, connection_manager, mock_receiver):
    """Test sending a command failure handling."""
    connection_manager._is_connected = True
    mock_receiver.command.side_effect = Exception("Command failed")

    result = await connection_manager.async_send_command("test-command")

    assert result is None
    assert not connection_manager.connected

@pytest.mark.asyncio
async def test_rate_limit(hass, connection_manager):
    """Test rate limiting."""
    connection_manager._is_connected = True
    connection_manager._last_command_time = hass.loop.time()

    with patch("asyncio.sleep") as mock_sleep:
        await connection_manager.async_send_command("test")
        mock_sleep.assert_awaited()

@pytest.mark.asyncio
async def test_reconnect_failure(hass, connection_manager, mock_receiver):
    """Test reconnection failure."""
    connection_manager._is_connected = False
    mock_receiver.command.side_effect = Exception("Connection failed")

    # Shorten backoff for test
    with patch("asyncio.sleep"):
        result = await connection_manager.async_send_command("test")

    assert result is None
    assert not connection_manager.connected

@pytest.mark.asyncio
async def test_close(hass, connection_manager, mock_receiver):
    """Test closing the connection."""
    await connection_manager.async_close()

    # Disconnect is run in executor, so we can't check if it was called directly on the mock
    # unless we mock add_executor_job, but the simpler check is _is_connected state
    assert not connection_manager.connected
