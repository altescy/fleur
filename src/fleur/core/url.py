import re
from typing import TypeAlias

from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, concat, ident, literal

from .expr import Expr, ensure_expr

PathValue: TypeAlias = str | int | float
"""A value that can fill a path parameter."""

_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _encoded(value: PathValue | Expr[PathValue]) -> ESTreeExpression:
    return call(ident("encodeURIComponent"), call(ident("String"), ensure_expr(value)))


class Url:
    @staticmethod
    def encode_component(value: str | Expr[str]) -> Expr[str]:
        """Percent-encode a single URL component, such as a query value or a data URL payload."""
        return Expr(call(ident("encodeURIComponent"), ensure_expr(value)))

    @staticmethod
    def path(template: str, **params: PathValue | Expr[PathValue]) -> Expr[str]:
        """Fill `{name}` placeholders, as in OpenAPI paths, with percent-encoded values.

        Every placeholder needs a parameter and every parameter a placeholder; a mismatch raises
        `ValueError` when the view or update is built, before any request is sent.
        """
        pieces = _PLACEHOLDER.split(template)
        literals, names = pieces[0::2], pieces[1::2]
        if any("{" in text or "}" in text for text in literals):
            raise ValueError(f"Url.path() template {template!r} has a brace outside a {{name}} placeholder")
        missing = sorted(set(names) - params.keys())
        unused = sorted(params.keys() - set(names))
        if missing or unused:
            details = [
                f"missing {', '.join(missing)}" if missing else "",
                f"unused {', '.join(unused)}" if unused else "",
            ]
            raise ValueError(f"Url.path() parameters do not match {template!r}: {'; '.join(d for d in details if d)}")

        expr: ESTreeExpression = literal(literals[0])
        for name, text in zip(names, literals[1:], strict=True):
            expr = concat(expr, _encoded(params[name]))
            if text:
                expr = concat(expr, literal(text))
        return Expr(expr)
