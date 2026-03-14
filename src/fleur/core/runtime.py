from fleur.js.ast import ESTreeExpression
from fleur.js.builder import call, ident, member_expr

from .names import RUNTIME_NAMESPACE, RuntimeFunctionName, RuntimeMethodName


def runtime_root() -> ESTreeExpression:
    return ident(RUNTIME_NAMESPACE)


def runtime_ref(*path: RuntimeFunctionName | RuntimeMethodName) -> ESTreeExpression:
    if not path:
        return runtime_root()

    expr: ESTreeExpression = runtime_root()
    for part in path:
        expr = member_expr(expr, part)
    return expr


def runtime_call(
    path: tuple[RuntimeFunctionName | RuntimeMethodName, ...], *args: ESTreeExpression
) -> ESTreeExpression:
    return call(runtime_ref(*path), *args)
