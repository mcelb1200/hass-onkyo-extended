"""Receiver profiles for Onkyo/Pioneer/Integra."""

from __future__ import annotations

RECEIVER_PROFILES = {
    "VSX-831": {
        "brand": "Pioneer",
        "eiscp_port": 60128,
        "ha_defaults": {
            "listening_modes": [
                "Stereo",
                "Direct",
                "Dolby Surround",
                "All Channel Stereo"
            ],
            "max_volume_percent": 55,
            "sources": {
                "bd": "Blu-ray",
                "cbl/sat": "Set-top Box",
                "game": "Game",
                "tv": "TV (ARC)",
                "net": "Network",
                "fm": "FM",
                "am": "AM",
                "phono": "Phono",
                "bluetooth": "Bluetooth",
                "cd": "CD"
            },
            "volume_resolution": None
        },
        "hdmi_outputs": {
            "dual_main_sub": False,
            "notes": "Single HDMI OUT with ARC; 4K/60 pass‑through generation.",
            "service_codes": []
        },
        "inputs_present": [
            "bd",
            "dvd",
            "cbl/sat",
            "game",
            "pc",
            "tv",
            "cd",
            "phono",
            "net",
            "fm",
            "am",
            "usb",
            "bluetooth"
        ],
        "listening_mode_families": [
            "Stereo",
            "Direct",
            "Dolby",
            "DTS",
            "AllChStereo",
            "Dolby Surround"
        ],
        "model": "VSX-831",
        "net_services": [],
        "product_page": [
            "https://www.manua.ls/pioneer/vsx-831/manual",
            "https://www.manualslib.com/manual/1100480/Pioneer-Vsx-831.html"
        ],
        "tuners": {
            "fm": True,
            "am": True,
            "dab": False
        },
        "zones": {
            "main": True,
            "zone2": False,
            "zone3": False,
            "zone_b": False
        }
    },
    "VSX-832": {
        "brand": "Pioneer",
        "eiscp_port": 60128,
        "ha_defaults": {
            "listening_modes": [
                "Stereo",
                "Direct",
                "Dolby Surround",
                "All Channel Stereo"
            ],
            "max_volume_percent": 55,
            "sources": {
                "bd": "Blu-ray",
                "cbl/sat": "Set-top Box",
                "strm box": "Streaming Box",
                "game": "Game",
                "tv": "TV (ARC)",
                "net": "Network",
                "fm": "FM",
                "am": "AM",
                "phono": "Phono",
                "bluetooth": "Bluetooth",
                "cd": "CD"
            },
            "volume_resolution": None
        },
        "hdmi_outputs": {
            "dual_main_sub": False,
            "notes": "Single HDMI OUT; 4K/60, BT.2020; HDR10/Dolby Vision pass‑through per generation.",
            "service_codes": []
        },
        "inputs_present": [
            "bd",
            "dvd",
            "cbl/sat",
            "strm box",
            "game",
            "pc",
            "tv",
            "cd",
            "phono",
            "net",
            "fm",
            "am",
            "usb",
            "bluetooth"
        ],
        "listening_mode_families": [
            "Stereo",
            "Direct",
            "Dolby",
            "DTS",
            "AllChStereo",
            "Dolby Surround"
        ],
        "model": "VSX-832",
        "net_services": [
            "chromecast",
            "dts_play_fi",
            "flareconnect"
        ],
        "product_page": [
            "https://intl.pioneer-av.com/vsx-832",
            "https://www.manualslib.com/manual/1248379/Pioneer-Vsx-832.html"
        ],
        "tuners": {
            "fm": True,
            "am": True,
            "dab": False
        },
        "zones": {
            "main": True,
            "zone2": False,
            "zone3": False,
            "zone_b": False
        }
    },
    "VSX-S520D": {
        "brand": "Pioneer",
        "eiscp_port": 60128,
        "ha_defaults": {
            "listening_modes": [
                "Stereo",
                "Direct",
                "Dolby Surround",
                "All Channel Stereo"
            ],
            "max_volume_percent": 50,
            "sources": {
                "bd": "Blu-ray",
                "cbl/sat": "Set-top Box",
                "strm box": "Streaming Box",
                "game": "Game",
                "tv": "TV (ARC)",
                "net": "Network",
                "dab": "DAB Radio",
                "fm": "FM Radio",
                "phono": "Phono",
                "usb": "USB",
                "bluetooth": "Bluetooth",
                "cd": "CD Player"
            },
            "volume_resolution": None
        },
        "hdmi_outputs": {
            "dual_main_sub": False,
            "notes": "Single HDMI OUT; 4K/60 4:4:4 pass‑through; BT.2020; HDR10 per generation.",
            "service_codes": []
        },
        "inputs_present": [
            "bd",
            "cbl/sat",
            "game",
            "strm box",
            "cd",
            "tv",
            "phono",
            "dab",
            "fm",
            "net",
            "usb",
            "bluetooth"
        ],
        "listening_mode_families": [
            "Stereo",
            "Direct",
            "Dolby",
            "DTS",
            "AllChStereo",
            "Dolby Surround"
        ],
        "model": "VSX-S520D",
        "net_services": [
            "chromecast",
            "dts_play_fi",
            "flareconnect"
        ],
        "product_page": [
            "https://intl.pioneer-audiovisual.com/products/av_receiver/vsx-s520d/index.php",
            "https://www.manualslib.com/manual/1201670/Pioneer-Vsx-S520d.html"
        ],
        "tuners": {
            "fm": True,
            "am": False,
            "dab": True
        },
        "zones": {
            "main": True,
            "zone2": False,
            "zone3": False,
            "zone_b": False
        }
    },
    "VSX-932": {
        "brand": "Pioneer",
        "eiscp_port": 60128,
        "ha_defaults": {
            "listening_modes": [
                "Stereo",
                "Direct",
                "Dolby Surround",
                "DTS Neural:X",
                "All Channel Stereo"
            ],
            "max_volume_percent": 55,
            "sources": {
                "bd": "Blu-ray",
                "cbl/sat": "Set-top Box",
                "game": "Game Console",
                "pc": "PC",
                "tv": "TV (ARC)",
                "net": "Network",
                "fm": "FM Radio",
                "am": "AM Radio",
                "phono": "Phono",
                "usb": "USB",
                "bluetooth": "Bluetooth",
                "cd": "CD Player"
            },
            "volume_resolution": None
        },
        "hdmi_outputs": {
            "dual_main_sub": False,
            "notes": "Single HDMI OUT (ARC); 4K/60, BT.2020, HDCP 2.2; HDR10 & Dolby Vision passtrough.",
            "service_codes": []
        },
        "inputs_present": [
            "bd",
            "dvd",
            "cbl/sat",
            "game",
            "pc",
            "tv",
            "cd",
            "phono",
            "net",
            "fm",
            "am",
            "usb",
            "bluetooth"
        ],
        "listening_mode_families": [
            "Stereo",
            "Direct",
            "Dolby",
            "DTS",
            "AllChStereo",
            "Dolby Surround",
            "DTS Neural:X"
        ],
        "model": "VSX-932",
        "net_services": [
            "chromecast",
            "dts_play_fi",
            "flareconnect"
        ],
        "product_page": [
            "https://intl.pioneer-audiovisual.com/products/av_receiver/vsx-932/",
            "https://pioneerhomeusa.com/vsx-932",
            "https://intl.pioneer-audiovisual.com/manuals/docs/SN29402804B_VSX-932_BAS_En_171113_web.pdf"
        ],
        "tuners": {
            "fm": True,
            "am": True,
            "dab": False
        },
        "zones": {
            "main": True,
            "zone2": False,
            "zone3": False,
            "zone_b": False
        }
    },
    "VSX-933": {
        "brand": "Pioneer",
        "eiscp_port": 60128,
        "ha_defaults": {
            "listening_modes": [
                "Stereo",
                "Direct",
                "Dolby Surround",
                "DTS Neural:X",
                "All Channel Stereo"
            ],
            "max_volume_percent": 55,
            "sources": {
                "bd": "Blu-ray",
                "cbl/sat": "Set-top Box",
                "game": "Game Console",
                "pc": "PC",
                "tv": "TV (ARC)",
                "net": "Network",
                "fm": "FM Radio",
                "am": "AM Radio",
                "phono": "Phono",
                "usb": "USB",
                "bluetooth": "Bluetooth",
                "cd": "CD Player"
            },
            "volume_resolution": None
        },
        "hdmi_outputs": {
            "dual_main_sub": False,
            "notes": "Single HDMI OUT with ARC; all HDMI ports support 4K/60, BT.2020, HDCP 2.2, HDR10/HLG/Dolby Vision passthrough.",
            "service_codes": []
        },
        "inputs_present": [
            "bd",
            "dvd",
            "cbl/sat",
            "game",
            "pc",
            "tv",
            "cd",
            "phono",
            "net",
            "fm",
            "am",
            "usb",
            "bluetooth"
        ],
        "listening_mode_families": [
            "Stereo",
            "Direct",
            "Dolby",
            "DTS",
            "AllChStereo",
            "Dolby Surround",
            "DTS Neural:X"
        ],
        "model": "VSX-933",
        "net_services": [
            "chromecast",
            "dts_play_fi",
            "flareconnect",
            "airplay",
            "spotify"
        ],
        "product_page": [
            "https://intl.pioneer-audiovisual.com/products/av_receiver/vsx-933/",
            "https://intl.pioneer-av.com/vsx-933",
            "https://www.manualslib.com/manual/1384477/Pioneer-Vsx-933.html"
        ],
        "tuners": {
            "fm": True,
            "am": True,
            "dab": False
        },
        "zones": {
            "main": True,
            "zone2": True,
            "zone3": False,
            "zone_b": False
        }
    },
    "VSX-LX101": {
        "brand": "Pioneer",
        "eiscp_port": 60128,
        "ha_defaults": {
            "listening_modes": [
                "Stereo",
                "Direct",
                "Dolby Surround",
                "DTS Neural:X",
                "All Channel Stereo"
            ],
            "max_volume_percent": 60,
            "sources": {
                "bd": "Blu-ray",
                "cbl/sat": "Set-top Box",
                "game": "Game",
                "pc": "PC",
                "tv": "TV (ARC)",
                "net": "Network",
                "fm": "FM",
                "am": "AM",
                "phono": "Phono",
                "bluetooth": "Bluetooth",
                "cd": "CD"
            },
            "volume_resolution": None
        },
        "hdmi_outputs": {
            "dual_main_sub": False,
            "notes": "Single HDMI OUT; inputs support 4K/60, HDCP 2.2; HDR/BT.2020 generation.",
            "service_codes": []
        },
        "inputs_present": [
            "bd",
            "dvd",
            "cbl/sat",
            "game",
            "pc",
            "tv",
            "cd",
            "phono",
            "net",
            "fm",
            "am",
            "usb",
            "bluetooth"
        ],
        "listening_mode_families": [
            "Stereo",
            "Direct",
            "Dolby",
            "DTS",
            "AllChStereo",
            "Dolby Surround",
            "DTS Neural:X"
        ],
        "model": "VSX-LX101",
        "net_services": [
            "chromecast",
            "airplay",
            "flareconnect"
        ],
        "product_page": [
            "https://intl.pioneer-audiovisual.com/products/av_receiver/vsx-lx101/",
            "https://www.snapav.com/wcsstore/ExtendedSitesCatalogAssetStore/attachments/documents/Pioneer/ManualsAndGuides/PE-VSX-LX101_Single%20Sheet.pdf",
            "https://www.manualslib.com/manual/1115059/Pioneer-Vsx-Lx101.html"
        ],
        "tuners": {
            "fm": True,
            "am": True,
            "dab": False
        },
        "zones": {
            "main": True,
            "zone2": False,
            "zone3": False,
            "zone_b": False
        }
    }
}
