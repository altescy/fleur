from collections.abc import Sequence

from fleur.core.array import Array
from fleur.core.cond import Cond
from fleur.core.expr import Expr, array
from fleur.core.types import KeyT


def toggle_selection(selected: Expr[Sequence[KeyT]], key: KeyT | Expr[KeyT]) -> Expr[Sequence[KeyT]]:
    return Cond.when(
        Array.includes(selected, key),
        Array.filter(selected, lambda item: Cond.not_equal(item, key)),
        Array.concat(selected, array([key])),
    )
