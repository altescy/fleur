def normalize_name(name: str | int) -> str:
    return str(name).strip().replace("_", "-")


def normalize_length(value: int | float | str) -> str:
    if isinstance(value, (int, float)):
        return f"{value}px"
    return value
