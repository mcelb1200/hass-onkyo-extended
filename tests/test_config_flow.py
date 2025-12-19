"""Tests for the Onkyo config flow."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.onkyo.const import CONF_RECEIVER_MAX_VOLUME, DOMAIN


@pytest.fixture(name="mock_setup_entry")
def mock_setup_entry():
    """Mock setting up a config entry."""
    with patch(
        "custom_components.onkyo.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup


@pytest.fixture(name="mock_eiscp")
def mock_eiscp():
    """Mock eISCP library."""
    with patch("custom_components.onkyo.config_flow.eISCP") as mock_eiscp:
        receiver = mock_eiscp.return_value
        receiver.command = MagicMock()
        receiver.model_name = "VSX-831"  # Default mock model
        yield mock_eiscp


@pytest.mark.asyncio
async def test_form(hass, mock_setup_entry, mock_eiscp):
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    # Test successful connection
    with patch(
        "custom_components.onkyo.config_flow.build_sources_list",
        return_value={"test": "Test Source"},
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "name": "Test Receiver",
                "receiver_max_volume": 80,
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Test Receiver"
    assert result2["data"] == {
        "host": "1.1.1.1",
        "name": "Test Receiver",
        "model_name": "VSX-831",
    }
    assert result2["options"]["receiver_max_volume"] == 80
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.asyncio
async def test_form_connect_timeout(hass, mock_eiscp):
    """Test connection timeout."""
    mock_eiscp.return_value.command.side_effect = TimeoutError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.onkyo.config_flow.build_sources_list",
        return_value={"test": "Test Source"},
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "name": "Test Receiver",
            },
        )

    # Should still create entry but log warning (allow setup)
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Test Receiver"


@pytest.mark.asyncio
async def test_form_connect_refused(hass, mock_eiscp):
    """Test connection refused."""
    mock_eiscp.return_value.command.side_effect = ConnectionRefusedError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.onkyo.config_flow.build_sources_list",
        return_value={"test": "Test Source"},
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "name": "Test Receiver",
            },
        )

    # Should still create entry
    assert result2["type"] == FlowResultType.CREATE_ENTRY


@pytest.mark.asyncio
async def test_form_import_error(hass):
    """Test library import error."""
    with patch("custom_components.onkyo.config_flow.eISCP", side_effect=ImportError):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "name": "Test Receiver",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "library_missing"}


@pytest.mark.asyncio
async def test_ssdp_discovery(hass, mock_setup_entry, mock_eiscp):
    """Test SSDP discovery."""

    discovery_info = {
        "host": "1.1.1.1",
        "friendlyName": "Onkyo Receiver._eISCP._tcp.local.",
    }

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_SSDP},
        data=discovery_info,
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"

    with patch(
        "custom_components.onkyo.config_flow.build_sources_list",
        return_value={"test": "Test Source"},
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={},
        )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Onkyo Receiver"
    assert result2["data"]["host"] == "1.1.1.1"


@pytest.mark.asyncio
async def test_options_flow(hass, mock_setup_entry):
    """Test options flow."""
    config_entry = config_entries.ConfigEntry(
        version=2,
        domain=DOMAIN,
        title="Test Receiver",
        data={"host": "1.1.1.1", "name": "Test Receiver"},
        source="user",
        options={CONF_RECEIVER_MAX_VOLUME: 80},
        discovery_keys={},
        unique_id="test_unique_id",
        minor_version=1,
    )
    hass.config_entries.async_update_entry = MagicMock()

    # Add the entry to hass
    await hass.config_entries.async_add(config_entry)

    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_RECEIVER_MAX_VOLUME: 100,
            "max_volume": 90,
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_RECEIVER_MAX_VOLUME] == 100


@pytest.mark.asyncio
async def test_options_flow_source_selection(hass):
    """Test that we can select sources in the options flow."""
    # Create a mock config entry with some initial sources
    initial_sources = {"video1": "Video 1", "video2": "Video 2"}

    config_entry = config_entries.ConfigEntry(
        version=2,
        domain=DOMAIN,
        title="Test Receiver",
        data={"host": "1.1.1.1", "name": "Test Receiver"},
        source="user",
        options={
            CONF_RECEIVER_MAX_VOLUME: 80,
            "sources": initial_sources,
        },
        discovery_keys={},
        unique_id="test_unique_id",
        minor_version=1,
    )
    hass.config_entries.async_update_entry = MagicMock()

    # Add the entry to hass
    await hass.config_entries.async_add(config_entry)

    # Mock build_sources_list to return a superset of sources
    all_sources = {
        "video1": "Video 1",
        "video2": "Video 2",
        "video3": "Video 3",
        "tape": "Tape Deck",
    }

    with patch(
        "custom_components.onkyo.config_flow.build_sources_list",
        return_value=all_sources,
    ):
        # Initialize options flow
        result = await hass.config_entries.options.async_init(config_entry.entry_id)

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "init"

        # Verify that CONF_SOURCES is in the data_schema
        schema = result["data_schema"]

        found_source_key = False
        for key in schema.schema:
            if key == "sources" or (hasattr(key, "schema") and key.schema == "sources"):
                found_source_key = True
                break

        assert found_source_key, "CONF_SOURCES field should be present in options flow"

        # Simulate user selecting only "video3" and "tape"
        user_input = {
            CONF_RECEIVER_MAX_VOLUME: 100,
            "max_volume": 90,
            "sources": ["video3", "tape"],
        }

        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input=user_input,
        )

        assert result2["type"] == FlowResultType.CREATE_ENTRY

        # Verify the options were updated correctly
        # The result should contain the DICTIONARY of selected sources
        expected_sources = {
            "video3": "Video 3",
            "tape": "Tape Deck",
        }
        assert result2["data"]["sources"] == expected_sources


@pytest.mark.asyncio
async def test_options_flow_default_all_sources(hass):
    """Test that all sources are selected by default if no configuration exists."""
    # Create a mock config entry with NO initial sources option
    config_entry = config_entries.ConfigEntry(
        version=2,
        domain=DOMAIN,
        title="Test Receiver",
        data={"host": "1.1.1.1", "name": "Test Receiver"},
        source="user",
        options={
            CONF_RECEIVER_MAX_VOLUME: 80,
            # CONF_SOURCES missing intentionally
        },
        discovery_keys={},
        unique_id="test_unique_id_2",
        minor_version=1,
    )

    await hass.config_entries.async_add(config_entry)

    all_sources = {
        "video1": "Video 1",
        "video2": "Video 2",
    }

    with patch(
        "custom_components.onkyo.config_flow.build_sources_list",
        return_value=all_sources,
    ):
        result = await hass.config_entries.options.async_init(config_entry.entry_id)
        assert result["type"] == FlowResultType.FORM

        # Inspect the schema to check the default value
        schema = result["data_schema"]

        # Helper to find the schema key and get its default value
        default_value = None
        for key in schema.schema:
            if key == "sources" or (hasattr(key, "schema") and key.schema == "sources"):
                default_value = key.default()
                break

        # Verify that the default value contains ALL keys
        assert set(default_value) == set(all_sources.keys())
