import dataclasses
import enum
from collections.abc import Mapping
from typing import Generic, Optional, TypeVar, Union

# ===== JavaScript Types =====


class JSType:
    """Base class for all JavaScript types."""


class Number(JSType):
    """Represents a JavaScript number type."""


class String(JSType):
    """Represents a JavaScript string type."""


class Boolean(JSType):
    """Represents a JavaScript boolean type."""


class Null(JSType):
    """Represents the JavaScript null type."""


class Undefined(JSType):
    """Represents the JavaScript undefined type."""


JSPrimitive = Union[Number, String, Boolean, Null, Undefined]


_JSTypeT = TypeVar("_JSTypeT", bound=JSType)
_JSTypeT_co = TypeVar("_JSTypeT_co", bound=JSType, covariant=True)


class Array(JSType, Generic[_JSTypeT_co]):
    """Represents a JavaScript array type containing elements of type _JSTypeT."""


class Object(JSType, Generic[_JSTypeT_co]):
    """Represents a JavaScript object type with properties of type _JSTypeT."""


class Function(JSType, Generic[_JSTypeT_co]):
    """Represents a JavaScript function type returning a type of _JSTypeT."""


# ===== AST Nodes =====


class Node:
    """Base class for all AST nodes."""


# ==== Expressions =====


class Expression(Node, Generic[_JSTypeT_co]):
    """Base class for all expression nodes."""


@dataclasses.dataclass(frozen=True)
class NumberLiteral(Expression[Number]):
    """Represents a numeric literal in the AST."""

    value: Union[int, float]


@dataclasses.dataclass(frozen=True)
class StringLiteral(Expression[String]):
    """Represents a string literal in the AST."""

    value: str


@dataclasses.dataclass(frozen=True)
class BooleanLiteral(Expression[Boolean]):
    """Represents a boolean literal in the AST."""

    value: bool


class NullLiteral(Expression[Null]):
    """Represents a null literal in the AST."""


class UndefinedLiteral(Expression[Undefined]):
    """Represents an undefined literal in the AST."""


@dataclasses.dataclass(frozen=True)
class ArrayLiteral(Expression[Array[_JSTypeT_co]], Generic[_JSTypeT_co]):
    """Represents an array literal in the AST."""

    elements: tuple[Expression[_JSTypeT_co], ...]


@dataclasses.dataclass(frozen=True)
class ObjectLiteral(Expression[Object[_JSTypeT_co]], Generic[_JSTypeT_co]):
    """Represents an object literal in the AST."""

    properties: Mapping[str, Expression[_JSTypeT_co]]


LiteralNode = Union[
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    NullLiteral,
    UndefinedLiteral,
    ArrayLiteral,
    ObjectLiteral,
]


@dataclasses.dataclass(frozen=True)
class Identifier(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents an identifier in the AST with type _JSTypeT."""

    name: str


class UnaryOperator(str, enum.Enum):
    NEGATE = "-"
    NOT = "!"


@dataclasses.dataclass(frozen=True)
class UnaryExpression(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents a unary expression in the AST."""

    operator: UnaryOperator
    operand: Expression[JSType]


class BinaryOperator(str, enum.Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    AND = "&&"
    OR = "||"
    EQUAL = "==="
    NOT_EQUAL = "!=="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="


@dataclasses.dataclass(frozen=True)
class BinaryExpression(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents a binary expression in the AST."""

    operator: BinaryOperator
    left: Expression[JSType]
    right: Expression[JSType]


@dataclasses.dataclass(frozen=True)
class CallExpression(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents a function call expression in the AST."""

    callee: Expression[Function[_JSTypeT]]
    arguments: tuple[Expression[JSType], ...]


@dataclasses.dataclass(frozen=True)
class PropertyAccessExpression(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents a property access expression in the AST."""

    object: Expression[JSType]
    property: str


@dataclasses.dataclass(frozen=True)
class KeyAccessExpression(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents a key access expression in the AST."""

    object: Expression[Object[_JSTypeT]]
    key: Expression[String]


@dataclasses.dataclass(frozen=True)
class AssignmentExpression(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents an assignment expression in the AST."""

    target: Expression[_JSTypeT]
    value: Expression[_JSTypeT]


@dataclasses.dataclass(frozen=True)
class FunctionExpression(Expression[Function[_JSTypeT_co]], Generic[_JSTypeT_co]):
    """Represents a function expression in the AST."""

    parameters: tuple[Identifier[JSType], ...]
    body: "BlockStatement"


@dataclasses.dataclass(frozen=True)
class ParenthesizedExpression(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents a parenthesized expression in the AST."""

    expression: Expression[_JSTypeT]


@dataclasses.dataclass(frozen=True)
class ConditionalExpression(Expression[_JSTypeT], Generic[_JSTypeT]):
    """Represents a conditional (ternary) expression in the AST."""

    condition: Expression[Boolean]
    consequent: Expression[_JSTypeT]
    alternate: Expression[_JSTypeT]


# ==== Statements =====


class Statement(Node):
    """Base class for all statement nodes."""


@dataclasses.dataclass(frozen=True)
class BlockStatement(Statement):
    """Represents a block statement in the AST."""

    statements: tuple[Statement, ...]


@dataclasses.dataclass(frozen=True)
class ExpressionStatement(Statement):
    """Represents an expression statement in the AST."""

    expression: Expression[JSType]


@dataclasses.dataclass(frozen=True)
class ReturnStatement(Statement, Generic[_JSTypeT]):
    """Represents a return statement in the AST."""

    argument: Optional[Expression[_JSTypeT]] = None


class VariableDeclarationKind(str, enum.Enum):
    VAR = "var"
    LET = "let"
    CONST = "const"


@dataclasses.dataclass(frozen=True)
class VariableDeclarationStatement(Statement, Generic[_JSTypeT]):
    """Represents a variable declaration in the AST."""

    kind: VariableDeclarationKind
    identifier: Identifier[_JSTypeT]
    initializer: Expression[_JSTypeT]


@dataclasses.dataclass(frozen=True)
class FunctionDeclarationStatement(Statement, Generic[_JSTypeT_co]):
    """Represents a function declaration in the AST."""

    name: str
    parameters: tuple[Identifier[JSType], ...]
    body: BlockStatement


@dataclasses.dataclass(frozen=True)
class IfStatement(Statement):
    """Represents an if statement in the AST."""

    condition: Expression[Boolean]
    consequent: BlockStatement
    alternate: Optional[BlockStatement] = None


@dataclasses.dataclass(frozen=True)
class ForStatement(Statement):
    """Represents a for statement in the AST."""

    initializer: Optional[Statement]
    condition: Optional[Expression[Boolean]]
    increment: Optional[Expression[JSType]]
    body: BlockStatement


@dataclasses.dataclass(frozen=True)
class ForOfStatement(Statement):
    """Represents a for...of statement in the AST."""

    iterator: Identifier[JSType]
    iterable: Expression[JSType]
    body: BlockStatement


@dataclasses.dataclass(frozen=True)
class ForInStatement(Statement):
    """Represents a for...in statement in the AST."""

    iterator: Identifier[String]
    object: Expression[Object[JSType]]
    body: BlockStatement


@dataclasses.dataclass(frozen=True)
class WhileStatement(Statement):
    """Represents a while statement in the AST."""

    condition: Expression[Boolean]
    body: BlockStatement


class BreakStatement(Statement):
    """Represents a break statement in the AST."""


class ContinueStatement(Statement):
    """Represents a continue statement in the AST."""
