"""Helpers to Onkyo media player."""

from __future__ import annotations

from typing import Any

from eiscp.commands import COMMANDS

from .onkyo_model_mapping import MODEL_SOURCES


def build_sources_list(model_name: str | None = None) -> dict:
    """
    Retrieve default sources from eISCP commands.

    Parses the eISCP command definitions to build a list of available
    source selection commands and their descriptions.

    Args:
        model_name: The model name of the receiver. If provided, returns only
                    sources supported by that model.

    Returns:
        dict: A dictionary mapping source identifiers to descriptions.
    """
    sources_list = {}
    model_specific_sources = None

    if model_name and model_name in MODEL_SOURCES:
        model_specific_sources = set(MODEL_SOURCES[model_name])

    for value in COMMANDS["main"]["SLI"]["values"].values():
        name = value["name"]
        desc = value["description"].replace("sets ", "")
        if isinstance(name, tuple):
            name = name[0]
        if name in ["07", "08", "09", "up", "down", "query"]:
            continue

        if model_specific_sources is not None:
            # Check if this source is in the model's supported list
            # The model_specific_sources contains the source name (not hex ID)
            if name not in model_specific_sources:
                continue

        sources_list.update({name: desc})
    return sources_list


def build_sounds_mode_list() -> dict:
    """
    Retrieve sound mode list from eISCP commands.

    Parses the eISCP command definitions to build a list of available
    sound mode commands.

    Returns:
        dict: A dictionary mapping sound mode identifiers to readable names.
    """
    sounds_list = []
    for value in COMMANDS["main"]["LMD"]["values"].values():
        name = value["name"]
        if isinstance(name, tuple):
            name = name[-1]
        if name in ["up", "down", "query"]:
            continue
        sounds_list.append(name)
    sounds_list = list(set(sounds_list))
    sounds_list.sort()
    return {name: name.replace("-", " ").title() for name in sounds_list}


def build_selected_dict(
    sources: dict[str, Any] | None = None, sounds: dict[str, Any] | None = None
) -> dict[str, str]:
    """
    Return selected dictionary filtered by provided keys.

    Args:
        sources: Optional dictionary of sources to filter by.
        sounds: Optional dictionary of sound modes to filter by.

    Returns:
        dict[str, str]: A filtered dictionary of sources or sound modes.
    """
    if sources:
        return {k: v for k, v in build_sources_list().items() if k in sources}
    if sounds:
        return {k: v for k, v in build_sounds_mode_list().items() if k in sounds}
    return {}


def reverse_mapping(ssdict) -> dict[str, str]:
    """
    Reverse dictionary mapping (value -> key).

    Args:
        ssdict: The dictionary to reverse.

    Returns:
        dict[str, str]: A new dictionary with keys and values swapped.
    """
    return {v: k for k, v in ssdict.items()}
