"""Tests for Onkyo helpers."""

import pytest
from unittest.mock import patch, MagicMock
from custom_components.onkyo import helpers

# Mock COMMANDS structure
MOCK_COMMANDS = {
    "main": {
        "SLI": {
            "values": {
                "01": {"name": "video1", "description": "sets video1"},
                "02": {"name": ("video2", "VCR"), "description": "sets video2"},
                "07": {"name": "07", "description": "sets 07"},  # Should be skipped
            }
        },
        "LMD": {
            "values": {
                "00": {"name": "stereo"},
                "01": {"name": ("direct", "Direct")},
                "up": {"name": "up"},  # Should be skipped
            }
        }
    }
}

def test_build_sources_list():
    """Test building sources list."""
    with patch.dict("custom_components.onkyo.helpers.COMMANDS", MOCK_COMMANDS):
        sources = helpers.build_sources_list()

        assert "video1" in sources
        assert sources["video1"] == "video1"
        assert "video2" in sources
        assert sources["video2"] == "video2"
        assert "07" not in sources

def test_build_sounds_mode_list():
    """Test building sound modes list."""
    with patch.dict("custom_components.onkyo.helpers.COMMANDS", MOCK_COMMANDS):
        modes = helpers.build_sounds_mode_list()

        assert "Stereo" in modes.values()
        assert "Direct" in modes.values()
        assert "up" not in modes

def test_build_selected_dict():
    """Test building selected dictionary."""
    with patch.dict("custom_components.onkyo.helpers.COMMANDS", MOCK_COMMANDS):
        # Test sources filter
        selected = helpers.build_selected_dict(sources={"video1": "ignored"})
        assert "video1" in selected
        assert "video2" not in selected

        # Test sounds filter
        selected = helpers.build_selected_dict(sounds={"stereo": "ignored"})
        assert "stereo" in selected
        assert "direct" not in selected

def test_reverse_mapping():
    """Test reverse mapping."""
    original = {"key": "value"}
    reversed_dict = helpers.reverse_mapping(original)
    assert reversed_dict == {"value": "key"}
