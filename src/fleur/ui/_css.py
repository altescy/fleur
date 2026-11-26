from dataclasses import dataclass
from typing import Generic

from typing_extensions import TypeVar

from fleur.core.expr import Expr

_CssT = TypeVar("_CssT", bound=str | Expr[str])
_CssT_co = TypeVar("_CssT_co", bound=str | Expr[str], covariant=True, default=str | Expr[str])


@dataclass(frozen=True, slots=True)
class CssValue(Generic[_CssT_co]):
    value: _CssT_co


def css(value: _CssT) -> CssValue[_CssT]:
    """Pass a literal or reactive CSS value to a token-aware shorthand."""
    return CssValue(value)


def color_reference(token: str) -> str:
    return token if token == "transparent" else f"var(--fleur-color-{token})"
