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
    GraineUndefinedNode,
)
from .jit import _GraineBuilder, as_interface, auto_let, require_block, use_block
from .types import (
    GraineArrayType,
    GraineBooleanLikeType,
    GraineBooleanType,
    GraineFunctionType,
    GraineNumberType,
    GraineObject,
    GraineStringType,
    GraineType,
    GraineTypeS_co,
    GraineTypeT,
    GraineTypeT_co,
    GraineUndefinedType,
    PyNumberCompat,
)


def case(
    condition: GraineObject[GraineASTExpr[GraineBooleanLikeType]],
) -> Callable[[Callable], None]:
    def decorator(func: Callable) -> None:
        block = require_block()
        with use_block() as inner:
            ret = func()
            if ret is not None:
                inner.emit(GraineReturnNode(value=ret.__graine_ast__))
        block.emit(
            GraineIfNode(
                condition=condition.__graine_ast__,
                then_branch=inner,
            )
        )

    return decorator


@auto_let
def when(
    condition: GraineObject[GraineASTExpr[GraineBooleanLikeType]],
    /,
    *,
    then: GraineObject[GraineASTExpr[GraineTypeS_co]],
    otherwise: Optional[GraineObject[GraineASTExpr[GraineTypeT_co]]] = None,
) -> GraineObject[GraineConditionalNode[Union[GraineTypeS_co, GraineTypeT_co, GraineUndefinedType]]]:
    return cast(
        GraineObject[GraineConditionalNode[Union[GraineTypeS_co, GraineTypeT_co, GraineUndefinedType]]],
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
    instance: GraineObject[GraineASTExpr[GraineTypeT]],
    cls: Union[type, GraineObject[GraineIdentifierNode]],
) -> GraineObject[GraineBinaryOpNode[GraineBooleanType]]:
    cls_ast = cls.__graine_ast__
    return cast(
        GraineObject[GraineBinaryOpNode[GraineBooleanType]],
        _GraineBuilder(
            GraineBinaryOpNode(
                op="instanceof",
                left=instance.__graine_ast__,
                right=cls_ast,
            )
        ),
    )


@auto_let
def typeof(
    instance: GraineObject[GraineASTExpr[GraineTypeT]],
) -> GraineObject[GraineASTExpr[GraineStringType]]:
    typeof_node = GraineCallNode(
        function=GraineIdentifierNode(name="typeof"),
        arguments=[instance.__graine_ast__],
    )
    return cast(
        GraineObject[GraineASTExpr[GraineStringType]],
        _GraineBuilder(typeof_node),
    )


def foreach(
    iterable: GraineObject[GraineASTExpr[GraineArrayType]],
    /,
) -> Callable[[Callable[[GraineObject[GraineASTExpr[GraineType]]], None]], None]:
    def decorator(func: Callable[[GraineObject[GraineASTExpr[GraineTypeT]]], None]) -> None:
        block = require_block()
        var = cast(GraineObject, _GraineBuilder(block.new_identifier()))

        with use_block() as inner:
            func(var)

        block.emit(
            GraineForOfNode(
                variable=var.__graine_ast__,
                iterator=iterable.__graine_ast__,
                body=inner,
            )
        )

    return decorator


class Object(GraineObject):
    def __init__(self) -> None: ...

    @staticmethod
    def getPrototypeOf(obj: GraineObject, /) -> GraineObject: ...


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


class Event(_GraineBuilder):
    __graine_ast__ = GraineIdentifierNode(name="Event")

    if TYPE_CHECKING:

        def __init__(self) -> None: ...

        @property
        def target(self) -> "EventTarget": ...

        @property
        def type(self) -> GraineObject[GraineASTExpr[GraineStringType]]: ...


class EventTarget(_GraineBuilder):
    def __init__(self) -> None:
        self.__graine_ast__ = GraineIdentifierNode(name="EventTarget")

    if TYPE_CHECKING:

        def __init__(self) -> None: ...

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
            name: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
            value: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
        ) -> None: ...

        @staticmethod
        def getAttribute(
            name: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
        ) -> GraineObject[GraineASTExpr[GraineStringType]]: ...


class Element(Node):
    __graine_ast__ = GraineIdentifierNode(name="Element")

    if TYPE_CHECKING:

        def __init__(self) -> None: ...

        @staticmethod
        def appendChild(
            child: "Node",
        ) -> GraineObject[GraineASTExpr[GraineType]]: ...

        @staticmethod
        def replaceWith(*nodes: "Node") -> GraineObject[GraineUndefinedNode]: ...


class CharacterData(Node):
    __graine_ast__ = GraineIdentifierNode(name="CharacterData")

    if TYPE_CHECKING:

        def __init__(
            self,
            text: Union[
                GraineObject[GraineASTExpr[GraineUndefinedType]],
                GraineObject[GraineASTExpr[GraineStringType]],
            ] = GraineObject[GraineUndefinedNode](),
        ) -> None: ...

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

    if TYPE_CHECKING:

        def __init__(self) -> None: ...

        @property
        def activeElement(self) -> GraineObject[GraineASTExpr[GraineType]]: ...

        @staticmethod
        def createTextNode(
            data: GraineObject[GraineASTExpr[GraineStringType]],
        ) -> "Text": ...

        @staticmethod
        def getElementById(
            element_id: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
        ) -> GraineObject[GraineASTExpr[GraineType]]: ...

        @staticmethod
        def getElementsByClassName(
            class_name: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
        ) -> GraineObject[GraineASTExpr[GraineArrayType]]: ...

        @staticmethod
        def createElement(
            tag_name: Union[str, GraineObject[GraineASTExpr[GraineStringType]]],
        ) -> GraineObject[GraineASTExpr[GraineType]]: ...
