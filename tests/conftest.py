"""Global fixtures for Onkyo tests."""

import pytest
from pytest_homeassistant_custom_component import common

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test directory."""
    yield


# Monkeypatch MockConfigEntry to be compatible with older Home Assistant versions
# (like 2024.3.3 used in CI) which do not support 'discovery_keys' in ConfigEntry.
_original_init = common.MockConfigEntry.__init__


def _patched_init(self, *args, **kwargs):
    # Remove 'discovery_keys' if present, as older HA versions don't support it
    # but pytest-homeassistant-custom-component (newer versions) passes it.
    kwargs.pop("discovery_keys", None)
    _original_init(self, *args, **kwargs)


common.MockConfigEntry.__init__ = _patched_init
