"""
Constants for the Onkyo integration.

This module defines constants used throughout the Onkyo custom component,
including configuration keys, defaults, connection settings, and attribute names.
"""

from typing import Final

# Domain
DOMAIN: Final = "onkyo"
"""The domain identifier for this integration."""

# Configuration
CONF_RECEIVER_MAX_VOLUME: Final = "receiver_max_volume"
"""Configuration key for the receiver's maximum absolute volume setting."""

CONF_VOLUME_RESOLUTION: Final = "volume_resolution"
"""Configuration key for volume resolution (steps)."""

CONF_MAX_VOLUME: Final = "max_volume"
"""Configuration key for the maximum volume limit (percentage)."""

CONF_SOURCES: Final = "sources"
"""Configuration key for the list of input sources."""

# Defaults
DEFAULT_NAME: Final = "Onkyo Receiver"
"""Default name for the receiver entity."""

DEFAULT_RECEIVER_MAX_VOLUME: Final = 100
"""Default maximum volume on the receiver."""

DEFAULT_VOLUME_RESOLUTION: Final = 80
"""Default volume resolution (number of steps)."""

# Volume resolution options (number of steps from min to max)
VOLUME_RESOLUTION_50: Final = 50
"""Volume resolution for very old receivers."""

VOLUME_RESOLUTION_80: Final = 80
"""Volume resolution for older Onkyo receivers."""

VOLUME_RESOLUTION_100: Final = 100
"""Volume resolution for some models."""

VOLUME_RESOLUTION_200: Final = 200
"""Volume resolution for newer Onkyo receivers."""

# Connection settings
CONNECTION_TIMEOUT: Final = 10
"""Timeout in seconds for initial connection attempts."""

RECONNECT_DELAY_BASE: Final = 1
"""Base delay in seconds for reconnection backoff."""

RECONNECT_DELAY_MAX: Final = 60
"""Maximum delay in seconds for reconnection backoff."""

COMMAND_DELAY: Final = 0.15
"""Delay in seconds between consecutive commands."""

# Service names
SERVICE_SELECT_HDMI_OUTPUT: Final = "select_hdmi_output"
"""Service name for selecting HDMI output."""

# Attributes
ATTR_HDMI_OUTPUT: Final = "hdmi_output"
"""Attribute key for HDMI output status."""

ATTR_AUDIO_INFORMATION: Final = "audio_information"
"""Attribute key for audio information."""

ATTR_VIDEO_INFORMATION: Final = "video_information"
"""Attribute key for video information."""

ATTR_PRESET: Final = "preset"
"""Attribute key for tuner preset."""

# HDMI Output options
HDMI_OUTPUT_OPTIONS: Final = [
    "no",
    "analog",
    "yes",
    "out",
    "out-sub",
    "sub",
    "hdbaset",
    "both",
    "up",
]
"""List of valid HDMI output options."""

# Update intervals
UPDATE_INTERVAL: Final = 30
"""Update interval in seconds for polling when push updates are not available."""

# Error messages
ERROR_CANNOT_CONNECT: Final = "cannot_connect"
"""Error string for connection failure."""

ERROR_TIMEOUT: Final = "timeout"
"""Error string for timeout."""

ERROR_UNKNOWN: Final = "unknown"
"""Error string for unknown errors."""

ERROR_INVALID_HOST: Final = "invalid_host"
"""Error string for invalid host."""

ERROR_NETWORK_ERROR: Final = "network_error"
"""Error string for network errors."""
