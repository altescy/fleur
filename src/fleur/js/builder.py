import contextvars
import inspect
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import TYPE_CHECKING, ClassVar, Final, Generic, Optional, TypeVar, Union, cast, final, overload

from typing_extensions import ParamSpec

from . import ast
from .transformer import _GET_CURRENT_BUILDER, create_transformed_function

_JSTypeT = TypeVar("_JSTypeT", bound=ast.JSType)


def _binary_operation(
    op: ast.BinaryOperator,
    left: Union[ast.Expression, "ExpressionBuilder"],
    right: Union[ast.Expression, "ExpressionBuilder"],
) -> ast.Expression:
    left_ast = left if isinstance(left, ast.Expression) else left.__fleur_js_ast__
    right_ast = right if isinstance(right, ast.Expression) else right.__fleur_js_ast__
    return ast.ParenthesizedExpression(ast.BinaryExpression(operator=op, left=left_ast, right=right_ast))


def _unary_operation(
    op: ast.UnaryOperator,
    operand: Union[ast.Expression, "ExpressionBuilder"],
) -> ast.Expression:
    operand_ast = operand if isinstance(operand, ast.Expression) else operand.__fleur_js_ast__
    return ast.UnaryExpression(operator=op, operand=operand_ast)


class ExpressionBuilder(Generic[_JSTypeT]):
    __fleur_js_ast__: ast.Expression[_JSTypeT]

    def __init__(self, ast_node: Union[ast.Expression[_JSTypeT], "ExpressionBuilder[_JSTypeT]"]) -> None:
        if isinstance(ast_node, ExpressionBuilder):
            ast_node = ast_node.__fleur_js_ast__
        self.__fleur_js_ast__ = ast_node

    if not TYPE_CHECKING:

        def __getitem__(self: "ExpressionBuilder[ast.Object]", key: "String") -> "ExpressionBuilder":
            return ExpressionBuilder(
                ast.KeyAccessExpression(
                    object=self.__fleur_js_ast__,
                    key=key.__fleur_js_ast__,
                )
            )

        def __getattr__(self, key: str) -> "ExpressionBuilder":
            return ExpressionBuilder(
                ast.PropertyAccessExpression(
                    object=self.__fleur_js_ast__,
                    property=key,
                )
            )

        def __call__(self: "ExpressionBuilder[ast.Function]", *args: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(
                ast.CallExpression(
                    callee=self.__fleur_js_ast__,
                    arguments=tuple(arg.__fleur_js_ast__ for arg in args),
                )
            )

        def __add__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.ADD, self, other))

        def __radd__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.ADD, other, self))

        def __sub__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.SUBTRACT, self, other))

        def __rsub__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.SUBTRACT, other, self))

        def __mul__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.MULTIPLY, self, other))

        def __rmul__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.MULTIPLY, other, self))

        def __truediv__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.DIVIDE, self, other))

        def __rtruediv__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.DIVIDE, other, self))

        def __neg__(self) -> "ExpressionBuilder":
            return ExpressionBuilder(_unary_operation(ast.UnaryOperator.NEGATE, self))

        def __not__(self) -> "ExpressionBuilder":
            return ExpressionBuilder(_unary_operation(ast.UnaryOperator.NOT, self))

        def __lt__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.LESS_THAN, self, other))

        def __le__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.LESS_EQUAL, self, other))

        def __gt__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return other.__lt__(self)

        def __ge__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return other.__le__(self)

        def __eq__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.EQUAL, self, other))

        def __ne__(self, other: "ExpressionBuilder") -> "ExpressionBuilder":
            return ExpressionBuilder(_binary_operation(ast.BinaryOperator.NOT_EQUAL, self, other))

        def __bool__(self) -> bool:
            raise TypeError("Cannot convert ExpressionBuilder to bool at runtime.")


_ExpressionBuilderT = TypeVar("_ExpressionBuilderT", bound=ExpressionBuilder)
_ExpressionBuilderT_co = TypeVar("_ExpressionBuilderT_co", bound=ExpressionBuilder, covariant=True)
_ExpressionBuilderU = TypeVar("_ExpressionBuilderU", bound=ExpressionBuilder)


@final
class Number(ExpressionBuilder[ast.Number]):
    def __init__(self, value: Union[int, float, ast.Expression[ast.Number], "Number"]) -> None:
        if isinstance(value, (int, float)):
            value = ast.NumberLiteral(value=value)
        super().__init__(value)

    if TYPE_CHECKING:

        def __add__(self, other: "Number") -> "Number": ...
        def __radd__(self, other: "Number") -> "Number": ...
        def __sub__(self, other: "Number") -> "Number": ...
        def __rsub__(self, other: "Number") -> "Number": ...
        def __mul__(self, other: "Number") -> "Number": ...
        def __rmul__(self, other: "Number") -> "Number": ...
        def __truediv__(self, other: "Number") -> "Number": ...
        def __rtruediv__(self, other: "Number") -> "Number": ...
        def __lt__(self, other: "Number") -> "Boolean": ...
        def __le__(self, other: "Number") -> "Boolean": ...
        def __gt__(self, other: "Number") -> "Boolean": ...
        def __ge__(self, other: "Number") -> "Boolean": ...
        def __eq__(self, other: "ExpressionBuilder") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def __ne__(self, other: "ExpressionBuilder") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def __neg__(self) -> "Number": ...
        def toExponential(self, fractionDigits: Optional["Number"] = ...) -> "String": ...
        def toFixed(self, digits: Optional["Number"] = ...) -> "String": ...
        def toPrecision(self, precision: Optional["Number"] = ...) -> "String": ...
        def toString(self, radix: Optional["Number"] = ...) -> "String": ...


@final
class String(ExpressionBuilder[ast.String]):
    def __init__(self, value: Union[str, ast.Expression[ast.String], "String"]) -> None:
        if isinstance(value, str):
            value = ast.StringLiteral(value=value)
        super().__init__(value)

    if TYPE_CHECKING:

        def __add__(self, other: "String") -> "String": ...
        def __radd__(self, other: "String") -> "String": ...
        def __eq__(self, other: "String") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def __ne__(self, other: "String") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def concat(self, *args: "String") -> "String": ...
        def endsWith(self, searchString: "String", endPosition: Number = ...) -> "Boolean": ...
        def includes(self, searchString: "String", position: Number = ...) -> "Boolean": ...
        def indexOf(self, searchString: "String", position: Number = ...) -> "Number": ...
        def padEnd(self, targetLength: Number, padString: "String" = ...) -> "String": ...
        def padStart(self, targetLength: Number, padString: "String" = ...) -> "String": ...
        def repeat(self, count: Number) -> "String": ...
        def replace(self, searchValue: "String", replaceValue: "String") -> "String": ...
        def replaceAll(self, searchValue: "String", replaceValue: "String") -> "String": ...
        def slice(self, start: Number, end: Optional[Number] = ...) -> "String": ...
        def split(self, separator: "String", limit: Optional[Number] = ...) -> 'Array["String"]': ...
        def startsWith(self, searchString: "String", position: Number = ...) -> "Boolean": ...
        def substring(self, start: Number, end: Optional[Number] = ...) -> "String": ...
        def toLowerCase(self) -> "String": ...
        def toUpperCase(self) -> "String": ...
        def trim(self) -> "String": ...
        def trimEnd(self) -> "String": ...
        def trimStart(self) -> "String": ...
        @property
        def length(self) -> "Number": ...


@final
class Boolean(ExpressionBuilder[ast.Boolean]):
    def __init__(self, value: Union[bool, ast.Expression[ast.Boolean], "Boolean"]) -> None:
        if isinstance(value, bool):
            value = ast.BooleanLiteral(value=value)
        super().__init__(value)

    if TYPE_CHECKING:

        def __not__(self) -> "Boolean": ...
        def __eq__(self, other: "Boolean") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def __ne__(self, other: "Boolean") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def toString(self) -> "String": ...


@final
class Null(ExpressionBuilder[ast.Null]):
    def __init__(self, value: Optional[ast.Expression[ast.Null]] = None) -> None:
        if value is None:
            value = ast.NullLiteral()
        super().__init__(value)

    if TYPE_CHECKING:

        def __eq__(self, other: "ExpressionBuilder") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def __ne__(self, other: "ExpressionBuilder") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def toString(self) -> "String": ...


@final
class Undefined(ExpressionBuilder[ast.Undefined]):
    def __init__(self, value: Optional[ast.Expression[ast.Undefined]] = None) -> None:
        if value is None:
            value = ast.UndefinedLiteral()
        super().__init__(value)

    if TYPE_CHECKING:

        def __eq__(self, other: "ExpressionBuilder") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]
        def __ne__(self, other: "ExpressionBuilder") -> "Boolean": ...  # pyright: ignore[reportIncompatibleMethodOverride]


@final
class Array(ExpressionBuilder[ast.Array], Generic[_ExpressionBuilderT_co]):
    def __init__(self, *value: _ExpressionBuilderT_co) -> None:
        self._builders: Sequence[_ExpressionBuilderT_co] = value
        self.__fleur_js_ast__ = ast.ArrayLiteral(elements=tuple(builder.__fleur_js_ast__ for builder in self._builders))

    if TYPE_CHECKING:

        def __getitem__(self, index: Number) -> _ExpressionBuilderT_co: ...
        @property
        def length(self) -> Number: ...
        def at(self, index: Number) -> _ExpressionBuilderT_co: ...
        def concat(self, *items: "Array[_ExpressionBuilderT_co]") -> "Array[_ExpressionBuilderT_co]": ...
        def every(self, callback: "Function[[_ExpressionBuilderT_co], Boolean]") -> Boolean: ...
        def filter(
            self, callback: "Function[[_ExpressionBuilderT_co], Boolean]"
        ) -> "Array[_ExpressionBuilderT_co]": ...
        def find(
            self, callback: "Function[[_ExpressionBuilderT_co], Boolean]"
        ) -> Union[_ExpressionBuilderT_co, Undefined]: ...
        def findIndex(self, callback: "Function[[_ExpressionBuilderT_co], Boolean]") -> Number: ...
        def findLast(
            self, callback: "Function[[_ExpressionBuilderT_co], Boolean]"
        ) -> Union[_ExpressionBuilderT_co, Undefined]: ...
        def findLastIndex(self, callback: "Function[[_ExpressionBuilderT_co], Boolean]") -> Number: ...
        def flat(self, depth: Optional[Number] = ...) -> "Array[_ExpressionBuilderT_co]": ...
        def flatMap(
            self, callback: "Function[[_ExpressionBuilderT_co], Array[_ExpressionBuilderT_co]]"
        ) -> "Array[_ExpressionBuilderT_co]": ...
        def forEach(self, callback: "Function[[_ExpressionBuilderT_co], Undefined]") -> Undefined: ...
        def map(
            self, callback: "Function[[_ExpressionBuilderT_co], _ExpressionBuilderU]"
        ) -> "Array[_ExpressionBuilderU]": ...
        def pop(self) -> Union[_ExpressionBuilderT_co, Undefined]: ...
        def push(self: "Array[_ExpressionBuilderT]", *items: _ExpressionBuilderT) -> Number: ...
        def reduce(
            self,
            callback: "Function[[_ExpressionBuilderU, _ExpressionBuilderT_co], _ExpressionBuilderU]",
            initialValue: Optional[_ExpressionBuilderU] = ...,
        ) -> _ExpressionBuilderU: ...
        def reverse(self) -> "Array[_ExpressionBuilderT_co]": ...
        def slice(self, start: Number, end: Optional[Number] = ...) -> "Array[_ExpressionBuilderT_co]": ...
        def some(self, callback: "Function[[_ExpressionBuilderT_co], Boolean]") -> Boolean: ...
        def sort(
            self, compareFn: Optional["Function[[_ExpressionBuilderT_co, _ExpressionBuilderT_co], Number]"] = ...
        ) -> "Array[_ExpressionBuilderT_co]": ...
        def toReversed(self) -> "Array[_ExpressionBuilderT_co]": ...
        def toSorted(
            self, compareFn: Optional["Function[[_ExpressionBuilderT_co, _ExpressionBuilderT_co], Number]"] = ...
        ) -> "Array[_ExpressionBuilderT_co]": ...
        def unshift(self: "Array[_ExpressionBuilderT]", *items: _ExpressionBuilderT) -> Number: ...


class Record(ExpressionBuilder[ast.Object], Generic[_ExpressionBuilderT_co]):
    __fleur_js_funcs__: ClassVar[Mapping[str, "Function"]] = {}

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        cls.__fleur_js_funcs__ = {}
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, staticmethod):
                attr_value = (
                    attr_value.__func__ if isinstance(attr_value.__func__, Function) else Function(attr_value.__func__)
                )
            if isinstance(attr_value, Function):
                cls.__fleur_js_funcs__[attr_name] = attr_value

    def __init__(self, **value: _ExpressionBuilderT_co) -> None:
        super().__init__(
            ast.ObjectLiteral(
                properties={
                    **{key: val.__fleur_js_ast__ for key, val in self.__fleur_js_funcs__.items()},
                    **{key: val.__fleur_js_ast__ for key, val in value.items()},
                }
            )
        )

    if TYPE_CHECKING:

        def __getitem__(self, key: String) -> _ExpressionBuilderT_co: ...
        def hasOwnProperty(self, key: String) -> Boolean: ...
        def isPrototypeOf(self, key: "ExpressionBuilder") -> Boolean: ...
        def propertyIsEnumerable(self, key: String) -> Boolean: ...


_RecordT = TypeVar("_RecordT", bound=Record)


_P = ParamSpec("_P")
_R = TypeVar("_R", bound=ExpressionBuilder)


class Function(ExpressionBuilder[ast.Function], Generic[_P, _R]):
    def __init__(self, fn: Callable[_P, _R], *, transform: bool = True) -> None:
        parameters = tuple(ast.Identifier(name=param.name) for param in inspect.signature(fn).parameters.values())
        body_builder = StatementBuilder()

        # Create placeholder Function object for recursive calls
        func_placeholder = cast(Function, ExpressionBuilder(ast.Identifier(name=fn.__name__)))

        def _set_placeholder(target: Callable) -> None:
            if target.__code__.co_freevars and target.__closure__:
                for i, var_name in enumerate(target.__code__.co_freevars):
                    if var_name == fn.__name__:
                        target.__closure__[i].cell_contents = func_placeholder

        # If transform=True, use AST transformation to allow natural Python syntax
        if transform:
            param_names = {param.name for param in inspect.signature(fn).parameters.values()}
            # Pass body_builder as the builder instance for the transformed function
            transformed_fn = create_transformed_function(fn, param_names)

            _set_placeholder(transformed_fn)

            def _build_body() -> None:
                _CURRENT_BUILDER.set(body_builder)
                # Update __fleur_builder__ in the transformed function's globals
                # to point to the correct builder instance
                transformed_fn.__globals__[_GET_CURRENT_BUILDER] = _CURRENT_BUILDER.get
                # Make the function name refer to the Function object for recursive calls
                transformed_fn.__globals__[fn.__name__] = func_placeholder
                transformed_fn(*(ExpressionBuilder(param) for param in parameters))  # pyright: ignore[reportCallIssue]

            ctx = contextvars.copy_context()
            ctx.run(_build_body)
        else:
            # Original behavior: no transformation
            # Handle recursive functions by updating closure cells
            _set_placeholder(fn)

            def _build_body() -> None:
                _CURRENT_BUILDER.set(body_builder)
                fn(*(ExpressionBuilder(param) for param in parameters))  # pyright: ignore[reportCallIssue]

            ctx = contextvars.copy_context()
            ctx.run(_build_body)

        super().__init__(
            ast.ParenthesizedExpression(
                ast.FunctionExpression(
                    parameters=parameters,
                    body=body_builder.block,
                )
            )
        )

    if TYPE_CHECKING:

        def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R: ...
        def toString(self) -> String: ...


class StatementBuilder:
    def __init__(self) -> None:
        self._statements: list[ast.Statement] = []

    @property
    def statements(self) -> tuple[ast.Statement, ...]:
        return tuple(self._statements)

    @property
    def block(self) -> ast.BlockStatement:
        return ast.BlockStatement(statements=self.statements)

    @contextmanager
    def context(self) -> Iterator["StatementBuilder"]:
        new_builder = StatementBuilder()
        token = _CURRENT_BUILDER.set(new_builder)
        try:
            yield new_builder
        finally:
            _CURRENT_BUILDER.reset(token)

    def _declare_variable(
        self,
        kind: ast.VariableDeclarationKind,
        name: Union[str, type[_RecordT]],
        value: Optional[ExpressionBuilder] = None,
    ) -> Union[ExpressionBuilder, _RecordT]:
        if isinstance(name, type) and issubclass(name, Record):
            value = name()
            name = name.__name__
        if value is None:
            value = Undefined()
        declaration = ast.VariableDeclarationStatement(
            kind=kind,
            identifier=ast.Identifier(name=name),
            initializer=value.__fleur_js_ast__,
        )
        self._statements.append(declaration)
        return ExpressionBuilder(ast.Identifier(name=name))

    @overload
    def let(self, name: str) -> ExpressionBuilder: ...
    @overload
    def let(self, name: str, value: _ExpressionBuilderT) -> _ExpressionBuilderT: ...
    @overload
    def let(self, name: type[_RecordT]) -> _RecordT: ...
    def let(
        self, name: Union[str, type[_RecordT]], value: Optional[ExpressionBuilder] = None
    ) -> Union[ExpressionBuilder, _RecordT]:
        return self._declare_variable(ast.VariableDeclarationKind.LET, name, value)

    @overload
    def const(self, name: str) -> ExpressionBuilder: ...
    @overload
    def const(self, name: str, value: _ExpressionBuilderT) -> _ExpressionBuilderT: ...
    @overload
    def const(self, name: type[_RecordT]) -> _RecordT: ...
    def const(
        self, name: Union[str, type[_RecordT]], value: Optional[ExpressionBuilder] = None
    ) -> Union[ExpressionBuilder, _RecordT]:
        return self._declare_variable(ast.VariableDeclarationKind.CONST, name, value)

    @overload
    def var(self, name: str) -> ExpressionBuilder: ...
    @overload
    def var(self, name: str, value: _ExpressionBuilderT) -> _ExpressionBuilderT: ...
    @overload
    def var(self, name: type[_RecordT]) -> _RecordT: ...
    def var(
        self, name: Union[str, type[_RecordT]], value: Optional[ExpressionBuilder] = None
    ) -> Union[ExpressionBuilder, _RecordT]:
        return self._declare_variable(ast.VariableDeclarationKind.VAR, name, value)

    def assign(
        self,
        target: ExpressionBuilder[_JSTypeT],
        value: ExpressionBuilder[_JSTypeT],
    ) -> None:
        assignment = ast.ExpressionStatement(
            expression=ast.AssignmentExpression(
                target=target.__fleur_js_ast__,
                value=value.__fleur_js_ast__,
            )
        )
        self._statements.append(assignment)

    @overload
    def ret(self) -> None: ...
    @overload
    def ret(self, value: _ExpressionBuilderT) -> _ExpressionBuilderT: ...
    def ret(
        self,
        value: Optional[_ExpressionBuilderT] = None,
    ) -> Optional[_ExpressionBuilderT]:
        return_statement = ast.ReturnStatement(argument=value.__fleur_js_ast__ if value is not None else None)
        self._statements.append(return_statement)
        return value

    def if_then_else(
        self,
        condition: ExpressionBuilder[ast.Boolean],
        consequent: Callable[["StatementBuilder"], Optional[Union[ExpressionBuilder, ast.BlockStatement]]],
        alternate: Optional[
            Callable[["StatementBuilder"], Optional[Union[ExpressionBuilder, ast.BlockStatement]]]
        ] = None,
    ) -> None:
        consequent_builder = StatementBuilder()
        result = consequent(consequent_builder)
        # If the callable returns a BlockStatement, use it directly
        # Otherwise, use the builder's block
        consequent_block = result if isinstance(result, ast.BlockStatement) else consequent_builder.block

        alternate_block: Optional[ast.BlockStatement] = None
        if alternate is not None:
            alternate_builder = StatementBuilder()
            alternate_result = alternate(alternate_builder)
            alternate_block = (
                alternate_result if isinstance(alternate_result, ast.BlockStatement) else alternate_builder.block
            )

        if_statement = ast.IfStatement(
            condition=condition.__fleur_js_ast__,
            consequent=consequent_block,
            alternate=alternate_block,
        )
        self._statements.append(if_statement)

    @overload
    def function(self, fn: Callable[_P, _R], *, transform: bool = ...) -> Function[_P, _R]: ...
    @overload
    def function(self, fn: Callable[..., None], *, transform: bool = ...) -> Function[..., Undefined]: ...
    def function(self, fn: Callable, *, transform: bool = False) -> Function:
        js_function_ast = Function(fn, transform=transform).__fleur_js_ast__
        assert isinstance(js_function_ast, ast.ParenthesizedExpression)
        js_function_ast = js_function_ast.expression
        assert isinstance(js_function_ast, ast.FunctionExpression)

        function_declaration = ast.FunctionDeclarationStatement(
            name=fn.__name__,
            parameters=js_function_ast.parameters,
            body=js_function_ast.body,
        )
        self._statements.append(function_declaration)

        return cast(Function, ExpressionBuilder(ast.Identifier(name=fn.__name__)))


_GLOBAL_BUILDER: Final[StatementBuilder] = StatementBuilder()
_CURRENT_BUILDER: Final[contextvars.ContextVar[StatementBuilder]] = contextvars.ContextVar(
    "CURRENT_BUILDER",
    default=_GLOBAL_BUILDER,
)


@contextmanager
def use_context(builder: Optional[StatementBuilder] = None) -> Iterator[StatementBuilder]:
    token = _CURRENT_BUILDER.set(builder or StatementBuilder())
    try:
        yield _CURRENT_BUILDER.get()
    finally:
        _CURRENT_BUILDER.reset(token)


@overload
def let(name: str) -> ExpressionBuilder: ...
@overload
def let(name: str, value: _ExpressionBuilderT) -> _ExpressionBuilderT: ...
@overload
def let(name: type[_RecordT]) -> _RecordT: ...
def let(
    name: Union[str, type[_RecordT]],
    value: Optional[ExpressionBuilder] = None,
    *,
    builder: Optional[StatementBuilder] = None,
) -> ExpressionBuilder:
    return (builder or _CURRENT_BUILDER.get()).let(name, value)  # pyright: ignore[reportArgumentType]


@overload
def const(name: str) -> ExpressionBuilder: ...
@overload
def const(name: str, value: _ExpressionBuilderT) -> _ExpressionBuilderT: ...
@overload
def const(name: type[_RecordT]) -> _RecordT: ...
def const(
    name: Union[str, type[_RecordT]],
    value: Optional[ExpressionBuilder] = None,
    *,
    builder: Optional[StatementBuilder] = None,
) -> Union[ExpressionBuilder, _RecordT]:
    return (builder or _CURRENT_BUILDER.get()).const(name, value)  # pyright: ignore[reportArgumentType]


@overload
def var(name: str) -> ExpressionBuilder: ...
@overload
def var(name: str, value: _ExpressionBuilderT) -> _ExpressionBuilderT: ...
@overload
def var(name: type[_RecordT]) -> _RecordT: ...
def var(
    name: Union[str, type[_RecordT]],
    value: Optional[ExpressionBuilder] = None,
    *,
    builder: Optional[StatementBuilder] = None,
) -> Union[ExpressionBuilder, _RecordT]:
    return (builder or _CURRENT_BUILDER.get()).var(name, value)  # pyright: ignore[reportArgumentType]


def assign(
    target: ExpressionBuilder[_JSTypeT],
    value: ExpressionBuilder[_JSTypeT],
    *,
    builder: Optional[StatementBuilder] = None,
) -> None:
    (builder or _CURRENT_BUILDER.get()).assign(target, value)


@overload
def ret(*, builder: Optional[StatementBuilder] = ...) -> None: ...
@overload
def ret(value: _ExpressionBuilderT, *, builder: Optional[StatementBuilder] = ...) -> _ExpressionBuilderT: ...
def ret(
    value: Optional[ExpressionBuilder] = None,
    *,
    builder: Optional[StatementBuilder] = None,
) -> Optional[ExpressionBuilder]:
    return (builder or _CURRENT_BUILDER.get()).ret(value)  # pyright: ignore[reportArgumentType]


def if_then_else(
    condition: ExpressionBuilder[ast.Boolean],
    consequent: Callable[[StatementBuilder], Optional[Union[ExpressionBuilder, ast.BlockStatement]]],
    alternate: Optional[Callable[[StatementBuilder], Optional[Union[ExpressionBuilder, ast.BlockStatement]]]] = None,
    *,
    builder: Optional[StatementBuilder] = None,
) -> None:
    (builder or _CURRENT_BUILDER.get()).if_then_else(condition, consequent, alternate)


_RecordT = TypeVar("_RecordT", bound=Record)
_RecordU = TypeVar("_RecordU", bound=Record)


@overload
def define(
    fn: Callable[_P, _R], *, builder: Optional[StatementBuilder] = ..., transform: bool = ...
) -> Function[_P, _R]: ...
@overload
def define(
    fn: Callable[..., None], *, builder: Optional[StatementBuilder] = ..., transform: bool = ...
) -> Function[..., Undefined]: ...
@overload
def define(
    *, builder: Optional[StatementBuilder] = ..., transform: bool = ...
) -> Callable[[Callable[_P, _R]], Function[_P, _R]]: ...
def define(
    fn: Optional[Callable] = None,
    *,
    builder: Optional[StatementBuilder] = None,
    transform: bool = True,
) -> Union[Function, _RecordT, Callable[[Union[Callable, type[_RecordT]]], Union[Function, _RecordT]]]:
    """
    Decorator to define a JavaScript function.

    Can be used with or without arguments:
    - @builder.function: uses default settings
    - @builder.function(transform=True): enables AST transformation

    Args:
        fn: The function to decorate (auto-provided when used as @builder.function)
        builder: Optional builder instance (defaults to current context)
        transform: If True, transforms Python syntax to builder API calls

    Returns:
        Function object or decorator function
    """

    def decorator(f: Callable) -> Function:
        if isinstance(f, Callable):
            return (builder or _CURRENT_BUILDER.get()).function(f, transform=transform)

    if fn is None:
        # Called with arguments: @builder.function(transform=True)
        # Return a decorator
        return decorator
    # Called without arguments: @builder.function
    return decorator(fn)


@overload
def function(fn: Callable[_P, _R], *, transform: bool = ...) -> Function[_P, _R]: ...
@overload
def function(fn: Callable[..., None], *, transform: bool = ...) -> Function[..., Undefined]: ...
@overload
def function(*, transform: bool = ...) -> Callable[[Callable[_P, _R]], Function[_P, _R]]: ...
def function(
    fn: Optional[Callable] = None, *, transform: bool = True
) -> Union[Function, Callable[[Callable], Function]]:
    """Decorator to define a function expression."""
    if fn is None:

        def decorator(f: Callable) -> Function:
            return Function(f, transform=transform)

        return decorator

    return Function(fn, transform=transform)


def conditional(
    condition: ExpressionBuilder[ast.Boolean],
    consequent: _ExpressionBuilderT,
    alternate: _ExpressionBuilderU,
) -> Union[_ExpressionBuilderT, _ExpressionBuilderU]:
    return cast(
        Union[_ExpressionBuilderT, _ExpressionBuilderU],
        ExpressionBuilder(
            ast.ParenthesizedExpression(
                ast.ConditionalExpression(
                    condition=condition.__fleur_js_ast__,
                    consequent=consequent.__fleur_js_ast__,
                    alternate=alternate.__fleur_js_ast__,
                )
            )
        ),
    )


def collect_statements(builder: Optional[StatementBuilder] = None) -> tuple[ast.Statement, ...]:
    return (builder or _CURRENT_BUILDER.get()).statements
