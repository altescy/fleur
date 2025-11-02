"""
Abstract Syntax Tree (AST) definitions for Graine DSL.

This module defines the intermediate representation (IR) used to represent
Graine code before it is emitted as JavaScript. All AST nodes inherit from
GraineASTNode and are categorized into expressions (GraineASTExpr) and
statements (GraineASTStmt).

The AST is fully typed, with expression nodes carrying type information
through generic type parameters that reference GraineType definitions.
"""

import dataclasses
from typing import Generic, Literal, Optional, Union

from typing_extensions import TypeVar

from .types import (
    GraineArrayType,
    GraineBooleanLikeType,
    GraineBooleanType,
    GraineClassType,
    GraineNumberType,
    GraineRecordType,
    GraineStringType,
    GraineType,
    GraineUndefinedType,
)

_GraineTypeS = TypeVar("_GraineTypeS", bound=GraineType)
_GraineTypeS_co = TypeVar("_GraineTypeS_co", bound=GraineType, covariant=True)
_GraineTypeT = TypeVar("_GraineTypeT", bound=GraineType)
_GraineTypeT_co = TypeVar("_GraineTypeT_co", bound=GraineType, covariant=True, default=GraineType)


class GraineASTNode:
    """Base class for all Graine AST nodes."""

    ...


class GraineASTExpr(GraineASTNode, Generic[_GraineTypeT_co]):
    """
    Base class for expression nodes that produce values.

    Expression nodes are typed with a covariant type parameter indicating
    the Graine type of the value they produce.
    """

    ...


class GraineASTStmt(GraineASTNode):
    """Base class for statement nodes that perform actions without producing values."""

    ...


class GraineUndefinedNode(GraineASTExpr[GraineUndefinedType]):
    """Represents the JavaScript 'undefined' value."""

    ...


@dataclasses.dataclass
class GraineBooleanNode(GraineASTExpr[GraineBooleanType]):
    """Boolean literal node (true/false)."""

    value: bool


@dataclasses.dataclass
class GraineNumberNode(GraineASTExpr[GraineNumberType]):
    """Numeric literal node (stored as float for JavaScript compatibility)."""

    value: float


@dataclasses.dataclass
class GraineStringNode(GraineASTExpr[GraineStringType]):
    """String literal node."""

    value: str


@dataclasses.dataclass
class GraineArrayNode(GraineASTExpr[GraineArrayType], Generic[_GraineTypeT_co]):
    """
    Array literal node.

    Represents JavaScript array literals like [1, 2, 3].
    The type parameter indicates the element type.
    """

    elements: list[GraineASTExpr[_GraineTypeT_co]] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GraineRecordNode(GraineASTExpr[GraineRecordType], Generic[_GraineTypeT_co]):
    """
    Object literal node.

    Represents JavaScript object literals like {x: 1, y: 2}.
    The type parameter indicates the value type for all fields.
    """

    fields: dict[str, GraineASTExpr[_GraineTypeT_co]] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class GraineBinaryOpNode(GraineASTExpr[_GraineTypeT_co]):
    """
    Binary operation node.

    Represents operations like +, -, *, /, ===, instanceof, etc.
    The result type is determined by the operation and operand types.
    """

    op: str
    left: GraineASTExpr
    right: GraineASTExpr


@dataclasses.dataclass
class GraineIdentifierNode(GraineASTExpr[_GraineTypeT_co]):
    """
    Identifier reference node.

    Represents variable or function names in the generated JavaScript.
    """

    name: str


@dataclasses.dataclass
class GraineCallNode(GraineASTExpr[_GraineTypeT_co]):
    """
    Function call node.

    Represents function invocations like func(arg1, arg2).
    The type parameter indicates the return type.
    """

    function: GraineASTExpr
    arguments: list[GraineASTExpr] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GrainePropertyAccessNode(GraineASTExpr[_GraineTypeT_co]):
    """
    Property access node.

    Represents property access like obj.prop.
    """

    property_name: str
    receiver: GraineASTExpr


@dataclasses.dataclass
class GraineIndexAccessNode(GraineASTExpr[_GraineTypeT_co]):
    """
    Index access node.

    Represents bracket notation access like arr[0] or obj["key"].
    """

    index: GraineASTExpr
    receiver: GraineASTExpr


@dataclasses.dataclass
class GraineConditionalNode(
    GraineASTExpr[Union[_GraineTypeS, _GraineTypeT, GraineUndefinedType]],
    Generic[_GraineTypeS, _GraineTypeT],
):
    """
    Ternary conditional expression node.

    Represents JavaScript ternary operator: condition ? then_branch : else_branch.
    If else_branch is None, it defaults to undefined.

    The result type is Union[S, T, Undefined] where:
    - S is the type of then_branch
    - T is the type of else_branch (defaults to GraineType if not specified)

    Note: The Union type annotation is correct semantically but requires type: ignore
    because pyright cannot verify that Union[S, T, Undefined] satisfies the GraineType bound
    when S and T are type variables. The actual runtime values will always satisfy this constraint.
    """

    condition: GraineASTExpr[GraineBooleanLikeType]
    then_branch: GraineASTExpr[_GraineTypeS]
    else_branch: Optional[GraineASTExpr[_GraineTypeT]] = None


@dataclasses.dataclass
class GraineConstructionNode(GraineASTExpr[GraineClassType]):
    """
    Class instantiation node.

    Represents 'new ClassName(args)' expressions.
    """

    class_name: str
    arguments: list[GraineASTExpr] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GraineLetNode(GraineASTStmt):
    """
    Variable declaration statement.

    Represents 'let identifier = value;' statements.
    """

    identifier: GraineIdentifierNode
    value: GraineASTExpr


@dataclasses.dataclass
class GraineAssignNode(GraineASTStmt):
    """
    Assignment statement.

    Represents 'identifier = value;' statements (without let/const).
    The identifier can be a simple name, property access, or index access.
    """

    identifier: GraineASTExpr
    value: GraineASTExpr


@dataclasses.dataclass
class GraineReturnNode(GraineASTStmt):
    """
    Return statement.

    Represents 'return value;' statements in functions.
    """

    value: GraineASTExpr


@dataclasses.dataclass
class GraineBlockNode(GraineASTStmt):
    """
    Block of statements.

    Represents a sequence of statements, typically the body of a function
    or control structure. Also serves as a statement collector during
    code generation.
    """

    statements: list[GraineASTStmt] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GraineFunctionNode(GraineASTStmt):
    """
    Function declaration.

    Represents 'function name(params) { body }' declarations.
    """

    name: str
    parameters: list["GraineIdentifierNode"] = dataclasses.field(default_factory=list)
    body: GraineBlockNode = dataclasses.field(default_factory=GraineBlockNode)


@dataclasses.dataclass
class GraineMethodNode(GraineASTStmt):
    """
    Class method definition.

    Represents a method in a class, which can be a regular method,
    getter, or setter.
    """

    name: str
    function: GraineFunctionNode
    accessor: Optional[Literal["get", "set"]] = None


@dataclasses.dataclass
class GraineClassNode(GraineASTStmt):
    """
    Class declaration.

    Represents ES6 class declarations with constructor and methods.
    """

    name: str
    constructor: Optional[GraineFunctionNode] = None
    methods: list[GraineMethodNode] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GraineForOfNode(GraineASTStmt):
    """
    For-of loop statement.

    Represents 'for (let variable of iterator) { body }' loops.
    """

    variable: GraineIdentifierNode
    iterator: GraineASTExpr[GraineArrayType]
    body: GraineBlockNode = dataclasses.field(default_factory=GraineBlockNode)


@dataclasses.dataclass
class GraineIfNode(GraineASTStmt):
    """
    If statement.

    Represents 'if (condition) { then_branch } else { else_branch }' statements.
    """

    condition: GraineASTExpr
    then_branch: GraineBlockNode = dataclasses.field(default_factory=GraineBlockNode)
    else_branch: Optional[Union[GraineBlockNode, "GraineIfNode"]] = None
