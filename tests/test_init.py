"""Tests for Onkyo init."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.exceptions import ConfigEntryNotReady
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.onkyo import (
    async_migrate_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.onkyo.const import DOMAIN


@pytest.fixture
def mock_entry():
    return MockConfigEntry(
        version=1,
        domain=DOMAIN,
        title="Test Receiver",
        data={"host": "1.1.1.1", "name": "Test Receiver"},
        source="user",
        options={},
        unique_id="test_unique_id",
    )


@pytest.mark.asyncio
async def test_setup_entry_success(hass, mock_entry):
    """Test successful entry setup."""
    mock_entry.add_to_hass(hass)
    with (
        patch("custom_components.onkyo.eISCP") as mock_eiscp,
        patch("custom_components.onkyo._test_connection", return_value=True),
        patch(
            "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups"
        ) as mock_forward,
    ):
        mock_eiscp.return_value = MagicMock()

        assert await async_setup_entry(hass, mock_entry)
        assert DOMAIN in hass.data
        assert mock_entry.entry_id in hass.data[DOMAIN]
        mock_forward.assert_called_once()


@pytest.mark.asyncio
async def test_setup_entry_timeout(hass, mock_entry):
    """Test setup with connection timeout."""
    mock_entry.add_to_hass(hass)
    with (
        patch("custom_components.onkyo.eISCP") as mock_eiscp,
        patch("custom_components.onkyo._test_connection", side_effect=TimeoutError),
        patch(
            "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups"
        ) as mock_forward,
    ):
        # Setup should succeed (allow offline setup)
        assert await async_setup_entry(hass, mock_entry)
        assert DOMAIN in hass.data
        mock_forward.assert_called_once()


@pytest.mark.asyncio
async def test_setup_entry_os_error(hass, mock_entry):
    """Test setup with network error."""
    mock_entry.add_to_hass(hass)
    with (
        patch("custom_components.onkyo.eISCP") as mock_eiscp,
        patch(
            "custom_components.onkyo._test_connection",
            side_effect=OSError("Network unreachable"),
        ),
        patch(
            "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups"
        ) as mock_forward,
    ):
        # Setup should succeed (allow offline setup)
        assert await async_setup_entry(hass, mock_entry)
        assert DOMAIN in hass.data
        mock_forward.assert_called_once()


@pytest.mark.asyncio
async def test_setup_entry_unexpected_error(hass, mock_entry):
    """Test setup with unexpected error."""
    mock_entry.add_to_hass(hass)
    with (
        patch("custom_components.onkyo.eISCP") as mock_eiscp,
        patch(
            "custom_components.onkyo._test_connection", side_effect=Exception("Boom")
        ),
    ):
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, mock_entry)


@pytest.mark.asyncio
async def test_unload_entry(hass, mock_entry):
    """Test unloading entry."""
    mock_entry.add_to_hass(hass)

    # Mock forward entry setups to avoid loading platform
    with (
        patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups"),
        patch("custom_components.onkyo.eISCP") as mock_eiscp,
        patch("custom_components.onkyo._test_connection", return_value=True),
    ):
        await async_setup_entry(hass, mock_entry)

    # Then unload
    with (
        patch(
            "custom_components.onkyo.connection.OnkyoConnectionManager.async_close"
        ) as mock_close,
        patch(
            "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
            return_value=True,
        ),
    ):
        assert await async_unload_entry(hass, mock_entry)
        mock_close.assert_awaited()
        assert mock_entry.entry_id not in hass.data.get(DOMAIN, {})


@pytest.mark.asyncio
async def test_migrate_entry_v1_to_v2(hass, mock_entry):
    """Test migrating entry from v1 to v2."""
    mock_entry.add_to_hass(hass)
    # Ensure version is 1 (set in fixture)
    assert mock_entry.version == 1

    with patch("custom_components.onkyo.helpers.build_sources_list", return_value={}):
        assert await async_migrate_entry(hass, mock_entry)

    # The entry in hass should be updated
    entry = hass.config_entries.async_get_entry(mock_entry.entry_id)
    assert entry.version == 2
    assert "receiver_max_volume" in entry.options
