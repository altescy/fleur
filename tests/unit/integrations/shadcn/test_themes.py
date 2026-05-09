import json

from fleur.integrations.shadcn.themes import (
    ShadcnRegistryItem,
    theme_from_shadcn_registry_item,
    theme_from_shadcn_registry_json,
)
from fleur.ui import theme_style_tag, theme_variables


class TestShadcnThemes:
    def test_theme_from_shadcn_registry_item_maps_light_tokens(self) -> None:
        item: ShadcnRegistryItem = {
            "cssVars": {
                "theme": {
                    "font-sans": '"Inter", sans-serif',
                    "font-mono": '"JetBrains Mono", monospace',
                    "radius": "0.5rem",
                },
                "light": {
                    "background": "oklch(0.92 0.01 90)",
                    "foreground": "oklch(0.23 0 0)",
                    "card": "oklch(0.95 0.01 90)",
                    "muted": "oklch(0.83 0.02 87)",
                    "muted-foreground": "oklch(0.47 0.01 85)",
                    "border": "oklch(0.84 0.02 87)",
                    "primary": "oklch(0.30 0 0)",
                    "primary-foreground": "oklch(0.91 0.01 99)",
                    "accent": "oklch(0.91 0.01 99)",
                    "accent-foreground": "oklch(0.30 0 0)",
                    "ring": "oklch(0.30 0 0)",
                    "spacing": "0.25rem",
                    "tracking-normal": "0.01em",
                },
            }
        }

        theme = theme_from_shadcn_registry_item(item)
        variables = theme_variables(theme)

        assert variables["--fleur-color-bg-canvas"] == "oklch(0.92 0.01 90)"
        assert variables["--fleur-color-accent-solid-bg"] == "oklch(0.30 0 0)"
        assert variables["--fleur-font-body"] == '"Inter", sans-serif'
        assert variables["--fleur-radius-md"] == "0.5rem"
        assert variables["--fleur-space-lg"] == "calc(0.25rem * 4)"
        assert variables["--tracking-normal"] == "0.01em"
        assert variables["--fleur-color-destructive"] == "oklch(0.577 0.245 27.325)"
        assert variables["--fleur-color-surface"] == "oklch(0.83 0.02 87)"

    def test_theme_from_shadcn_registry_json_parses_payload(self) -> None:
        payload = json.dumps(
            {
                "cssVars": {
                    "theme": {},
                    "light": {
                        "background": "oklch(1 0 0)",
                        "foreground": "oklch(0.145 0 0)",
                    },
                }
            }
        )

        theme = theme_from_shadcn_registry_json(payload)
        variables = theme_variables(theme)

        assert variables["--fleur-color-bg-canvas"] == "oklch(1 0 0)"
        assert variables["--fleur-color-fg-default"] == "oklch(0.145 0 0)"

    def test_shadcn_registry_css_block_is_included_in_style_tag(self) -> None:
        item: ShadcnRegistryItem = {
            "cssVars": {
                "theme": {},
                "light": {
                    "background": "oklch(1 0 0)",
                    "foreground": "oklch(0.145 0 0)",
                },
            },
            "css": {
                "@layer base": {
                    "body": {
                        "letter-spacing": "var(--tracking-normal)",
                    }
                }
            },
        }
        theme = theme_from_shadcn_registry_item(item)

        css = theme_style_tag(theme)

        assert "@layer base{body{letter-spacing:var(--tracking-normal);}}" in css
