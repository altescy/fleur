from __future__ import annotations

from .base import Theme

ZEN_THEME = Theme(
    theme={
        "font-sans": '"Inter", sans-serif',
        "font-serif": '"Playfair Display", serif',
        "font-mono": '"JetBrains Mono", monospace',
        "radius": "0.5rem",
        "spacing": "0.25rem",
        "tracking-normal": "0.01em",
    },
    light={
        "background": "oklch(0.9195 0.0169 88.0030)",
        "foreground": "oklch(0.2350 0 0)",
        "card": "oklch(0.9530 0.0156 86.4257)",
        "card-foreground": "oklch(0.2350 0 0)",
        "popover": "oklch(0.9530 0.0156 86.4257)",
        "popover-foreground": "oklch(0.2350 0 0)",
        "primary": "oklch(0.3012 0 0)",
        "primary-foreground": "oklch(0.9169 0.0175 99.6160)",
        "secondary": "oklch(0.8647 0.0201 87.5232)",
        "secondary-foreground": "oklch(0.3012 0 0)",
        "muted": "oklch(0.8340 0.0232 87.1630)",
        "muted-foreground": "oklch(0.4688 0.0136 84.5932)",
        "accent": "oklch(0.9169 0.0175 99.6160)",
        "accent-foreground": "oklch(0.3012 0 0)",
        "border": "oklch(0.8434 0.0231 87.1621)",
        "input": "oklch(0.8434 0.0231 87.1621)",
        "ring": "oklch(0.3012 0 0)",
        "spacing": "0.25rem",
    },
    font_sizes={
        "xs": "0.75rem",
        "sm": "0.875rem",
        "base": "1rem",
        "lg": "1.125rem",
        "xl": "1.25rem",
        "2xl": "1.5rem",
    },
)
