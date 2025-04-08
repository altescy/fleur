from itertools import product
from typing import Final


def _spacing_utilities() -> dict[str, dict[str, str]]:
    units = [0.0, 0.25, 0.5, 0.75, 1, 1.5, 2, 4, 8]
    rems = {f"{int(u * 4)}": f"{u}rem" for u in units}
    props = ["m", "mt", "mb", "ml", "mr", "mx", "my", "p", "pt", "pb", "pl", "pr", "px", "py"]
    css: dict[str, dict[str, str]] = {}
    for prop, size in product(props, rems):
        value = rems[size]
        if prop.startswith("m"):
            css[f"{prop}-{size}"] = {"margin": value} if prop == "m" else {f"margin-{_direction(prop)}": value}
        else:
            css[f"{prop}-{size}"] = {"padding": value} if prop == "p" else {f"padding-{_direction(prop)}": value}
    return css


def _direction(shorthand) -> str:
    return {"t": "top", "b": "bottom", "l": "left", "r": "right", "x": ["left", "right"], "y": ["top", "bottom"]}[
        shorthand[-1]
    ]


def _size_utilities() -> dict[str, dict[str, str]]:
    units = [0, 1, 2, 4, 8, 16, 24, 32, 40, 48, 64, 80, 96, 128, 256]
    return (
        {f"w-{u}": {"width": f"{u}px"} for u in units}
        | {f"h-{u}": {"height": f"{u}px"} for u in units}
        | {
            "w-full": {"width": "100%"},
            "h-full": {"height": "100%"},
            "w-fit": {"width": "fit-content"},
            "h-fit": {"height": "fit-content"},
            "w-auto": {"width": "auto"},
            "h-auto": {"height": "auto"},
            "w-screen": {"width": "100vw"},
            "h-screen": {"height": "100vh"},
            "max-w-screen-sm": {"max-width": "640px"},
            "max-w-screen-md": {"max-width": "768px"},
            "max-w-screen-lg": {"max-width": "1024px"},
            "max-w-screen-xl": {"max-width": "1280px"},
            "max-w-screen-2xl": {"max-width": "1536px"},
            "max-h-screen-md": {"max-height": "768px"},
            "max-h-screen-lg": {"max-height": "1024px"},
            "max-h-screen-xl": {"max-height": "1280px"},
            "max-h-screen-2xl": {"max-height": "1536px"},
        }
    )


def _typography_utilities() -> dict[str, dict[str, str]]:
    return {
        "text-xs": {"font-size": "0.75rem"},
        "text-sm": {"font-size": "0.875rem"},
        "text-base": {"font-size": "1rem"},
        "text-lg": {"font-size": "1.125rem"},
        "text-xl": {"font-size": "1.25rem"},
        "font-light": {"font-weight": "300"},
        "font-normal": {"font-weight": "400"},
        "font-bold": {"font-weight": "700"},
        "leading-tight": {"line-height": "1.25"},
        "leading-relaxed": {"line-height": "1.625"},
        "text-center": {"text-align": "center"},
        "text-left": {"text-align": "left"},
        "text-right": {"text-align": "right"},
    }


def _border_utilities() -> dict[str, dict[str, str]]:
    return {
        "border": {"border-width": "1px"},
        "border-2": {"border-width": "2px"},
        "border-4": {"border-width": "4px"},
        "border-8": {"border-width": "8px"},
        "rounded": {"border-radius": "0.25rem"},
        "rounded-md": {"border-radius": "0.375rem"},
        "rounded-lg": {"border-radius": "0.5rem"},
        "rounded-full": {"border-radius": "9999px"},
    }


def _color_utilities() -> dict[str, dict[str, str]]:
    colors = {
        "gray": {"100": "#f3f4f6", "300": "#d1d5db", "800": "#1f2937"},
        "blue": {"100": "#dbeafe", "500": "#3b82f6", "700": "#1d4ed8"},
        "red": {"100": "#fee2e2", "500": "#ef4444", "700": "#b91c1c"},
        "green": {"100": "#bbf7d0", "500": "#22c55e", "700": "#16a34a"},
        "yellow": {"100": "#fef9c3", "500": "#eab308", "700": "#ca8a04"},
        "purple": {"100": "#e9d5ff", "500": "#a855f7", "700": "#9333ea"},
        "pink": {"100": "#fbcfe8", "500": "#ec4899", "700": "#db2777"},
        "indigo": {"100": "#e0f2fe", "500": "#6366f1", "700": "#4f46e5"},
        "teal": {"100": "#ccfbf1", "500": "#14b8a6", "700": "#0d9488"},
        "orange": {"100": "#fdba74", "500": "#f97316", "700": "#c2410c"},
        "lime": {"100": "#d9f99d", "500": "#84cc16", "700": "#65a30d"},
        "cyan": {"100": "#cffafe", "500": "#06b6d4", "700": "#0891b2"},
        "amber": {"100": "#fefcbf", "500": "#f59e0b", "700": "#b45309"},
        "rose": {"100": "#ffe4e6", "500": "#ec4899", "700": "#be123c"},
        "slate": {"100": "#f8fafb", "500": "#64748b", "700": "#475569"},
    }
    css = {}
    for name, shades in colors.items():
        for shade, hex in shades.items():
            css[f"text-{name}-{shade}"] = {"color": hex}
            css[f"bg-{name}-{shade}"] = {"background-color": hex}
            css[f"border-{name}-{shade}"] = {"border-color": hex}
    return css


def _layout_utilities() -> dict[str, dict[str, str]]:
    units = [0, 1, 2, 4, 8, 16, 24, 32, 40, 48, 64]
    return {
        "flex": {"display": "flex"},
        "grid": {"display": "grid"},
        "items-center": {"align-items": "center"},
        "items-start": {"align-items": "flex-start"},
        "items-end": {"align-items": "flex-end"},
        "justify-start": {"justify-content": "flex-start"},
        "justify-center": {"justify-content": "center"},
        "justify-end": {"justify-content": "flex-end"},
        "justify-between": {"justify-content": "space-between"},
        "flex-col": {"flex-direction": "column"},
        "flex-row": {"flex-direction": "row"},
        "flex-wrap": {"flex-wrap": "wrap"},
        "flex-nowrap": {"flex-wrap": "nowrap"},
        **{f"gap-{u}": {"gap": f"{u}px"} for u in units},
        **{f"gap-x-{u}": {"column-gap": f"{u}px"} for u in units},
        **{f"gap-y-{u}": {"row-gap": f"{u}px"} for u in units},
    }


def _shadow_utilities() -> dict[str, dict[str, str]]:
    return {
        "shadow": {"box-shadow": "0 1px 3px rgba(0,0,0,0.1)"},
        "shadow-md": {"box-shadow": "0 4px 6px rgba(0,0,0,0.1)"},
        "shadow-lg": {"box-shadow": "0 10px 15px rgba(0,0,0,0.1)"},
    }


def _transition_utilities() -> dict[str, dict[str, str]]:
    return {
        "transition": {"transition": "all 0.2s ease-in-out"},
        "duration-300": {"transition-duration": "300ms"},
        "ease-in": {"transition-timing-function": "ease-in"},
        "ease-out": {"transition-timing-function": "ease-out"},
    }


def _misc_utilities() -> dict[str, dict[str, str]]:
    return {
        "cursor-pointer": {"cursor": "pointer"},
        "overflow-auto": {"overflow": "auto"},
        "overflow-hidden": {"overflow": "hidden"},
        "overflow-visible": {"overflow": "visible"},
        "overflow-scroll": {"overflow": "scroll"},
        "overflow-x-auto": {"overflow-x": "auto"},
        "overflow-x-hidden": {"overflow-x": "hidden"},
        "overflow-x-visible": {"overflow-x": "visible"},
        "overflow-x-scroll": {"overflow-x": "scroll"},
        "overflow-y-auto": {"overflow-y": "auto"},
        "overflow-y-hidden": {"overflow-y": "hidden"},
        "overflow-y-visible": {"overflow-y": "visible"},
        "overflow-y-scroll": {"overflow-y": "scroll"},
        "z-0": {"z-index": "0"},
        "z-10": {"z-index": "10"},
        "z-50": {"z-index": "50"},
        "z-100": {"z-index": "100"},
    }


def _generate_css_class(name, styles) -> str:
    rules = ""
    for prop, val in styles.items():
        if isinstance(prop, list):  # mx, myなど
            for p in prop:
                rules += f"  margin-{p}: {val};\n"
        else:
            rules += f"  {prop}: {val};\n"
    return f".{name} {{\n{rules}}}"


def _build_all_styles() -> dict[str, dict[str, str]]:
    all_utils = {}
    for func in [
        _spacing_utilities,
        _size_utilities,
        _typography_utilities,
        _border_utilities,
        _color_utilities,
        _layout_utilities,
        _shadow_utilities,
        _transition_utilities,
        _misc_utilities,
    ]:
        all_utils.update(func())
    return all_utils


def _generate_all_css() -> str:
    styles = _build_all_styles()
    return "\n".join(_generate_css_class(name, rule) for name, rule in styles.items())


DEFAULT_CSS: Final = _generate_all_css()
