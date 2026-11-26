from fleur.js.builder import call, ident

from .expr import Expr, ensure_expr


class Url:
    @staticmethod
    def encode_component(value: str | Expr[str]) -> Expr[str]:
        """Percent-encode a single URL component, such as a query value or a data URL payload."""
        return Expr(call(ident("encodeURIComponent"), ensure_expr(value)))
