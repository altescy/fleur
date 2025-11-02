from collections.abc import Callable
from typing import TYPE_CHECKING, Optional, Union, cast

from .ast import (
    GraineASTExpr,
    GraineBinaryOpNode,
    GraineCallNode,
    GraineConditionalNode,
    GraineForOfNode,
    GraineIdentifierNode,
    GraineIfNode,
    GraineReturnNode,
    GraineStringNode,
    GraineUndefinedNode,
)
from .jit import (
    _GraineBuilder,
    as_interface,
    auto_let,
    emit_statement,
    ensure_graine,
    new_identifier,
    require_block,
    use_block,
)
from .types import (
    GraineArray,
    GraineArrayType,
    GraineBoolean,
    GraineBooleanLike,
    GraineBooleanType,
    GraineFunction,
    GraineFunctionType,
    GraineNumber,
    GraineNumberType,
    GraineObject,
    GraineObjectS,
    GraineObjectT,
    GraineRecord,
    GraineRecordType,
    GraineString,
    GraineStringType,
    GraineType,
    GraineUndefinedType,
    PyBooleanCompat,
    PyNumberCompat,
)


def case(
    condition: Union[PyBooleanCompat, GraineBooleanLike],
) -> Callable[[Callable], None]:
    def decorator(func: Callable) -> None:
        nonlocal condition

        condition = ensure_graine(condition)
        block = require_block()
        with use_block() as inner:
            ret = func()
            if ret is not None:
                emit_statement(inner, GraineReturnNode(value=ret.__graine_ast__))
        emit_statement(
            block,
            GraineIfNode(
                condition=condition.__graine_ast__,
                then_branch=inner,
            ),
        )

    return decorator


@auto_let
def when(
    condition: GraineBooleanLike,
    /,
    *,
    then: GraineObjectS,
    otherwise: Optional[GraineObjectT] = None,
) -> Union[GraineObjectS, GraineObjectT]:
    return cast(
        Union[GraineObjectS, GraineObjectT],
        _GraineBuilder(
            GraineConditionalNode(
                condition=condition.__graine_ast__,
                then_branch=then.__graine_ast__,
                else_branch=otherwise.__graine_ast__ if otherwise is not None else None,
            )
        ),
    )


@auto_let
def instanceof(
    instance: GraineObject,
    cls: type[GraineObject],
) -> GraineBoolean:
    if isinstance(cls, type) and issubclass(cls, GraineBoolean):
        return cast(
            GraineBoolean,
            _GraineBuilder(
                GraineBinaryOpNode(
                    op="===",
                    left=GraineCallNode(
                        function=GraineIdentifierNode("typeof"),
                        arguments=[instance.__graine_ast__],
                    ),
                    right=GraineStringNode("boolean"),
                ),
            ),
        )
    if isinstance(cls, type) and issubclass(cls, GraineNumber):
        return cast(
            GraineBoolean,
            _GraineBuilder(
                GraineBinaryOpNode(
                    op="===",
                    left=GraineCallNode(
                        function=GraineIdentifierNode(name="typeof"),
                        arguments=[instance.__graine_ast__],
                    ),
                    right=GraineStringNode("number"),
                ),
            ),
        )
    if isinstance(cls, type) and issubclass(cls, GraineString):
        return cast(
            GraineBoolean,
            _GraineBuilder(
                GraineBinaryOpNode(
                    op="===",
                    left=GraineCallNode(
                        function=GraineIdentifierNode(name="typeof"),
                        arguments=[instance.__graine_ast__],
                    ),
                    right=GraineIdentifierNode("string"),
                ),
            ),
        )
    if isinstance(cls, type) and issubclass(cls, GraineUndefinedNode):
        return cast(
            GraineBoolean,
            _GraineBuilder(
                GraineBinaryOpNode(
                    op="===",
                    left=GraineCallNode(
                        function=GraineIdentifierNode(name="typeof"),
                        arguments=[instance.__graine_ast__],
                    ),
                    right=GraineStringNode("undefined"),
                ),
            ),
        )
    if isinstance(cls, type) and issubclass(cls, GraineFunction):
        return cast(
            GraineBoolean,
            _GraineBuilder(
                GraineBinaryOpNode(
                    op="===",
                    left=GraineCallNode(
                        function=GraineIdentifierNode(name="typeof"),
                        arguments=[instance.__graine_ast__],
                    ),
                    right=GraineStringNode("function"),
                ),
            ),
        )
    if isinstance(cls, type) and issubclass(cls, GraineArray):
        cls_ast = GraineIdentifierNode(name="Array")
    elif isinstance(cls, type) and issubclass(cls, GraineRecord):
        cls_ast = GraineIdentifierNode(name="Object")
    else:
        cls_ast = getattr(cls, "__graine_ast__", None)
        if cls_ast is None:
            raise TypeError(f"Cannot use instanceof with non-Graine class {cls}")
    return cast(
        GraineBoolean,
        _GraineBuilder(
            GraineBinaryOpNode(
                op="instanceof",
                left=instance.__graine_ast__,
                right=cls_ast,
            )
        ),
    )


@auto_let
def typeof(instance: GraineObject) -> GraineString:
    typeof_node = GraineCallNode(
        function=GraineIdentifierNode(name="typeof"),
        arguments=[instance.__graine_ast__],
    )
    return cast(GraineString, _GraineBuilder(typeof_node))


def foreach(
    iterable: GraineArray[GraineObjectT],
) -> Callable[[Callable[[GraineObjectT], None]], None]:
    def decorator(func: Callable[[GraineObjectT], None]) -> None:
        block = require_block()
        var = _GraineBuilder(new_identifier())

        with use_block() as inner:
            func(cast(GraineObjectT, var))

        emit_statement(
            block,
            GraineForOfNode(
                variable=var.__graine_ast__,
                iterator=iterable.__graine_ast__,
                body=inner,
            ),
        )

    return decorator


class cases:
    def __init__(self) -> None:
        self._ast: Optional[GraineIfNode] = None
        self._last: Optional[GraineIfNode] = None

    def __enter__(self) -> "cases":
        self._ast = None
        self._last = None
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._ast is not None:
            emit_statement(
                require_block(),
                self._ast,
            )

    def when(self, condition: Union[PyBooleanCompat, GraineBooleanLike]) -> Callable[[Callable], None]:
        def decorator(func: Callable) -> None:
            nonlocal condition

            condition = ensure_graine(condition)
            with use_block() as inner:
                ret = func()
                if ret is not None:
                    emit_statement(inner, GraineReturnNode(value=ret.__graine_ast__))

            new_if_node = GraineIfNode(
                condition=condition.__graine_ast__,
                then_branch=inner,
                else_branch=None,
            )

            if self._last is None:
                self._ast = new_if_node
                self._last = new_if_node
            else:
                self._last.else_branch = new_if_node
                self._last = new_if_node

        return decorator

    def otherwise(self, func: Callable) -> None:
        with use_block() as inner:
            ret = func()
            if ret is not None:
                emit_statement(inner, GraineReturnNode(value=ret.__graine_ast__))

        if self._last is None:
            self._ast = GraineIfNode(
                condition=GraineIdentifierNode("true"),
                then_branch=inner,
                else_branch=None,
            )
        else:
            self._last.else_branch = inner


@as_interface
class Math(GraineObject):
    @staticmethod
    def sqrt(
        value: Union[PyNumberCompat, GraineObject[GraineASTExpr[GraineNumberType]]],
    ) -> GraineObject[GraineASTExpr[GraineNumberType]]: ...


@as_interface
class JSON(GraineObject):
    @staticmethod
    def parse(
        text: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
    ) -> GraineObject[GraineASTExpr[GraineType]]: ...

    @staticmethod
    def stringify(
        value: GraineObject[GraineASTExpr[GraineType]],
    ) -> GraineObject[GraineASTExpr[GraineStringType]]: ...


class Proxy(_GraineBuilder, GraineObject[GraineIdentifierNode]):
    __graine_ast__ = GraineIdentifierNode(name="Proxy")

    def __init__(
        self,
        target: GraineObject[GraineASTExpr[GraineType]],
        handler: GraineObject[GraineASTExpr[GraineRecordType]],
    ) -> None: ...


class Event(_GraineBuilder, GraineObject[GraineIdentifierNode]):
    __graine_ast__ = GraineIdentifierNode(name="Event")

    def __init__(self) -> None: ...

    if TYPE_CHECKING:

        @property
        def target(self) -> "EventTarget": ...

        @property
        def type(self) -> GraineObject[GraineASTExpr[GraineStringType]]: ...


class EventTarget(
    _GraineBuilder[GraineIdentifierNode],
    GraineObject[GraineIdentifierNode],
):
    __graine_ast__ = GraineIdentifierNode(name="EventTarget")

    def __init__(self) -> None: ...

    if TYPE_CHECKING:

        def addEventListener(
            self,
            type: Union[str, GraineObject],
            listener: GraineObject[GraineASTExpr[GraineFunctionType]],
            options: Optional[GraineObject] = None,
        ) -> GraineObject[GraineUndefinedNode]: ...

        def dispatchEvent(
            self,
            event: Event,
        ) -> GraineObject[GraineASTExpr[GraineBooleanType]]: ...

        def removeEventListener(
            self,
            type: Union[str, GraineObject],
            listener: GraineObject[GraineASTExpr[GraineFunctionType]],
            options: Optional[GraineObject] = None,
        ) -> GraineObject[GraineUndefinedNode]: ...


class Node(EventTarget):
    __graine_ast__ = GraineIdentifierNode(name="Node")

    if TYPE_CHECKING:

        @staticmethod
        def setAttribute(
            name: GraineObject[GraineASTExpr[GraineStringType]],
            value: GraineObject,
        ) -> None: ...

        @staticmethod
        def getAttribute(
            name: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
        ) -> GraineObject[GraineASTExpr[GraineStringType]]: ...

        @staticmethod
        def removeAttribute(
            name: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
        ) -> GraineObject[GraineASTExpr[GraineUndefinedType]]: ...

        @property
        def parentNode(self) -> "Node": ...

        @property
        def firstChild(self) -> "Node": ...

        @property
        def lastChild(self) -> "Node": ...

        @property
        def childNodes(self) -> GraineArray: ...


class Element(Node):
    __graine_ast__ = GraineIdentifierNode(name="Element")

    def __init__(self) -> None: ...

    if TYPE_CHECKING:

        @staticmethod
        def appendChild(
            child: "Node",
        ) -> GraineObject[GraineASTExpr[GraineType]]: ...

        @staticmethod
        def replaceWith(*nodes: "Node") -> GraineObject[GraineUndefinedNode]: ...


class CharacterData(Node):
    __graine_ast__ = GraineIdentifierNode(name="CharacterData")

    def __init__(
        self,
        text: Union[
            GraineObject[GraineASTExpr[GraineUndefinedType]],
            GraineObject[GraineASTExpr[GraineStringType]],
        ] = GraineObject[GraineUndefinedNode](),
    ) -> None: ...

    if TYPE_CHECKING:

        @property
        def data(self) -> GraineObject[GraineASTExpr[GraineStringType]]: ...

        @data.setter
        def data(
            self,
            value: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
        ) -> None: ...


class Text(CharacterData):
    __graine_ast__ = GraineIdentifierNode(name="Text")


class Document(Node):
    __graine_ast__ = GraineIdentifierNode(name="Document")

    def __init__(self) -> None: ...

    if TYPE_CHECKING:

        @property
        def activeElement(self) -> GraineObject[GraineASTExpr[GraineType]]: ...

        @staticmethod
        def createTextNode(
            data: GraineObject[GraineASTExpr[GraineStringType]],
        ) -> "Text": ...

        @staticmethod
        def getElementById(
            element_id: GraineObject[GraineASTExpr[GraineStringType]],
        ) -> GraineObject[GraineASTExpr[GraineType]]: ...

        @staticmethod
        def getElementsByClassName(
            class_name: GraineObject[GraineASTExpr[GraineStringType]],
        ) -> GraineObject[GraineASTExpr[GraineArrayType]]: ...

        @staticmethod
        def createElement(
            tag_name: GraineObject[GraineASTExpr[GraineStringType]],
        ) -> Element: ...
