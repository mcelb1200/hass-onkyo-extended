
import pytest
from custom_components.onkyo.helpers import build_sources_list
from custom_components.onkyo.onkyo_model_mapping import MODEL_SOURCES
from eiscp.commands import COMMANDS

# Test with a known model
def test_build_sources_list_known_model():
    model = "TX-NR609(Ether)"
    # TX-NR609(Ether) sources include '10' (DVD/BD) and '01' (VIDEO2/CBL/SAT)
    # The output of build_sources_list is a dict {name: description}

    sources = build_sources_list(model)

    # Assertions should check for the names
    assert 'dvd' in sources
    assert 'video2' in sources

    # Verify filtering worked - check for a source NOT in this model
    # MODEL_SOURCES contains names.
    # Note: MODEL_SOURCES values are mapped via SOURCE_SETS in the actual file,
    # but the import gives the resolved list if implemented correctly?
    # Let's check onkyo_model_mapping.py structure.
    # It exports MODEL_SOURCES as a dict mapping model -> list of sources.
    # So MODEL_SOURCES[model] is a list of strings.

    supported_names = set(MODEL_SOURCES[model])

    # Find a source name that is available in COMMANDS but NOT in supported_names
    excluded_name = None
    for value in COMMANDS["main"]["SLI"]["values"].values():
        name = value["name"]
        if isinstance(name, tuple):
            name = name[0]

        if name in ["07", "08", "09", "up", "down", "query"]:
            continue

        if name not in supported_names:
            excluded_name = name
            break

    if excluded_name:
        assert excluded_name not in sources, f"Source {excluded_name} should be excluded for {model}"

def test_build_sources_list_unknown_model():
    model = "UnknownModel"
    sources = build_sources_list(model)
    # Should return all sources (except default excluded ones)

    all_sources = build_sources_list()
    assert len(sources) == len(all_sources)
    assert len(sources) > 0

def test_build_sources_list_no_model():
    sources = build_sources_list()
    assert len(sources) > 0
