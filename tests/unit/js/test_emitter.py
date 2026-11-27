from fleur.core import Expr
from fleur.js import emit
from fleur.js.ast import ESTreeUnaryExpression
from fleur.js.builder import ident, literal


def test_minus_before_negative_operand_does_not_form_decrement() -> None:
    x = Expr[int](ident("x"))

    assert emit((x - (-1)).__compile__()) == "(x- -1)"
    assert emit(ESTreeUnaryExpression(operator="-", argument=literal(-1), prefix=True)) == "(- -1)"


def test_operators_stay_compact_when_tokens_cannot_merge() -> None:
    x = Expr[int](ident("x"))

    assert emit((x - 1).__compile__()) == "(x-1)"
    assert emit((x + (-1)).__compile__()) == "(x+-1)"
