"""Catppuccin Mocha design tokens shared across the desktop client."""

from __future__ import annotations

from dataclasses import dataclass


# ---------- Colours ----------

BACKGROUND = "#11111B"
SURFACE = "#181825"
SURFACE_LIGHT = "#1E1E2E"
SURFACE_ELEVATED = "#1A1A2A"
INPUT = "#313244"
ACCENT = "#89B4FA"
ACCENT_HOVER = "#74C7EC"
TEXT = "#CDD6F4"
TEXT_SECONDARY = "#A6ADC8"
SUCCESS = "#A6E3A1"
WARNING = "#F9E2AF"
ERROR = "#F38BA8"
BORDER = "#45475A"

# ---------- Fonts ----------

FONT_FAMILY = "Inter"
FONT_MONO = "JetBrains Mono"

FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_HEADING = (FONT_FAMILY, 14, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_MONO_BODY = (FONT_MONO, 10)

# ---------- Layout ----------

WINDOW_WIDTH = 920
WINDOW_HEIGHT = 820
SIDEBAR_WIDTH = 240
RADIUS = 14
SMALL_RADIUS = 8
PADDING = 16
SPACING = 12
HEADER_HEIGHT = 60
INPUT_HEIGHT = 48

# ---------- Status ----------

ONLINE = SUCCESS
OFFLINE = ERROR
CONNECTING = WARNING

# ---------- Message Bubbles ----------

USER_BUBBLE = ACCENT
USER_TEXT = "#11111B"
PATRICK_BUBBLE = SURFACE_LIGHT
PATRICK_TEXT = TEXT
CODE_BG = "#11111B"
CODE_TEXT = "#CDD6F4"
INLINE_CODE_BG = "#313244"
INLINE_CODE_TEXT = "#F5E0DC"


@dataclass(frozen=True)
class ThemePalette:
    background: str = BACKGROUND
    surface: str = SURFACE
    surface_light: str = SURFACE_LIGHT
    accent: str = ACCENT
    text: str = TEXT
    text_secondary: str = TEXT_SECONDARY
    border: str = BORDER
    input: str = INPUT


THEME = ThemePalette()
