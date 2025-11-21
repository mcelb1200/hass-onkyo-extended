"""Global fixtures for Onkyo tests."""
import pytest
import pytest_homeassistant_custom_component.common as common
from unittest.mock import patch

pytest_plugins = "pytest_homeassistant_custom_component"

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test directory."""
    yield
