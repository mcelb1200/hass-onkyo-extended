# Onkyo Network Receiver Integration for Home Assistant

A robust Home Assistant custom component for Onkyo network receivers, utilizing the eISCP protocol. This integration provides a seamless way to control your Onkyo receiver directly from Home Assistant, offering enhanced reliability, multi-zone support, and comprehensive media control.

## Features

- **Robust Connection Handling**: Uses a dedicated connection manager with exponential backoff for automatic reconnection.
- **Multi-Zone Support**: Automatically detects and controls Main, Zone 2, and Zone 3.
- **Source & Mode Management**: Dynamically retrieves input sources and listening modes from the receiver.
- **Advanced Volume Control**: Accurate volume scaling and resolution handling (50, 80, 100, or 200 steps).
- **Custom Services**: Specific services for HDMI output selection and other advanced features.
- **Fixes for Recent HA Issues**: Addresses breaking changes in Home Assistant 2024.9+ and concurrency issues.

## Installation

### HACS (Recommended)

1.  Ensure [HACS](https://hacs.xyz/) is installed.
2.  Add this repository as a custom repository in HACS.
3.  Search for "Onkyo" and install the integration.
4.  Restart Home Assistant.

### Manual Installation

1.  Download the `custom_components/onkyo` folder from this repository.
2.  Copy the folder to your Home Assistant `custom_components/` directory.
3.  Restart Home Assistant.

## Configuration

Configuration is done entirely via the Home Assistant UI.

1.  Go to **Settings** > **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for **Onkyo**.
4.  Enter your receiver's IP address (or wait for discovery).
5.  Follow the prompts to configure basic settings.

### Options

After installation, you can configure additional options by clicking "Configure" on the integration entry:

- **Max Volume**: Set a safe maximum volume limit (percentage) to prevent accidental deafening.
- **Receiver Max Volume**: The maximum volume number displayed on your receiver's screen (e.g., 80, 100).
- **Volume Resolution**: The number of volume steps your receiver supports (usually 50, 80, 100, or 200).

## Usage

### Media Player Entity

The integration creates a `media_player` entity for each detected zone (e.g., `media_player.onkyo_receiver`, `media_player.onkyo_receiver_zone_2`).

**Supported Features:**

- Power On/Off
- Volume Up/Down/Mute/Set
- Source Selection
- Sound Mode Selection (Listening Modes)
- Play Media (Radio Presets)

### Custom Services

**`onkyo.select_hdmi_output`**
Selects the HDMI output for the main zone.

**Parameters:**

- `entity_id`: The entity ID of the main zone media player.
- `hdmi_output`: One of `no`, `analog`, `yes`, `out`, `out-sub`, `sub`, `hdbaset`, `both`, `up`.

## Troubleshooting

- **Missing Sources/Modes**: If sources or listening modes are missing, ensure the receiver is powered on. The integration attempts to fetch these dynamically.
- **Connection Issues**: If the receiver becomes unavailable, the integration will automatically attempt to reconnect. Check your network connection and receiver IP.
- **Logs**: Enable debug logging for `custom_components.onkyo` to see detailed connection and command information.

```yaml
logger:
  default: info
  logs:
    custom_components.onkyo: debug
```

## Development

### Project Structure

- `custom_components/onkyo/`: Main component source code.
  - `__init__.py`: Component setup and migration logic.
  - `config_flow.py`: UI configuration flow.
  - `media_player.py`: Media player entity implementation.
  - `connection.py`: connection handling logic.
  - `const.py`: Constants and configuration keys.
  - `coordinator.py`: Data update coordinator.
  - `helpers.py`: Utility functions.

### Contributing

Contributions are welcome! Please submit Pull Requests with clear descriptions of changes.

## License

This project is licensed under the GPL3 License.
