from re import fullmatch


def normalize_length(value: int | float | str) -> str:
    if isinstance(value, (int, float)):
        return f"{value}px"
    return value


def css_color(value: str) -> str:
    # Older shadcn palettes store bare HSL channels for hsl(var(--primary)).
    if fullmatch(r"[+-]?[\d.]+\s+[\d.]+%\s+[\d.]+%", value):
        return f"hsl({value})"
    return value


def scope_variable(name: str) -> str:
    return f"--fleur-scope-{name.removeprefix('--')}"
