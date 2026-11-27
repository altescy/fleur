import dataclasses
from collections.abc import Sequence
from typing import Generic, Literal

from typing_extensions import TypeVar

from fleur.types import JsonValue


@dataclasses.dataclass(slots=True)
class ESTreeNode: ...


@dataclasses.dataclass(slots=True)
class ESTreePattern(ESTreeNode):
    pass


@dataclasses.dataclass(slots=True)
class ESTreeExpression(ESTreeNode):
    pass


@dataclasses.dataclass(slots=True)
class ESTreeStatement(ESTreeNode):
    pass


ESTreeExpressionT = TypeVar("ESTreeExpressionT", bound=ESTreeExpression, default=ESTreeExpression)
ESTreeStatementT = TypeVar("ESTreeStatementT", bound=ESTreeStatement, default=ESTreeStatement)


##
## Identifiers
##


@dataclasses.dataclass(slots=True)
class ESTreeIdentifier(ESTreePattern, ESTreeExpression):
    name: str


@dataclasses.dataclass(slots=True)
class ESTreeGeneratedIdentifier(ESTreeIdentifier):
    """A lexical binding whose name is assigned once per emission."""

    name: str = ""


##
## Literals
##


@dataclasses.dataclass(slots=True)
class ESTreeLiteral(ESTreeExpression):
    value: JsonValue


##
## Prograsm
##


@dataclasses.dataclass(slots=True)
class ESTreeProgram(ESTreeNode):
    body: Sequence["ESTreeDirective | ESTreeStatement"]


##
## Functions
##


ESTreeFunctionIDT = TypeVar("ESTreeFunctionIDT", bound=ESTreeIdentifier | None, default=ESTreeIdentifier | None)


@dataclasses.dataclass(slots=True)
class ESTreeFunction(ESTreeExpression, Generic[ESTreeFunctionIDT]):
    id: ESTreeFunctionIDT
    params: Sequence[ESTreePattern]
    body: "ESTreeFunctionBody"


##
## Statements
##


@dataclasses.dataclass(slots=True)
class ESTreeExpressionStatement(ESTreeStatement, Generic[ESTreeExpressionT]):
    expression: ESTreeExpressionT


@dataclasses.dataclass(slots=True)
class ESTreeDirective(ESTreeExpressionStatement[ESTreeLiteral]):
    directive: str


@dataclasses.dataclass(slots=True)
class ESTreeBlockStatement(ESTreeStatement, Generic[ESTreeStatementT]):
    body: Sequence[ESTreeStatementT]


@dataclasses.dataclass(slots=True)
class ESTreeFunctionBody(ESTreeBlockStatement[ESTreeDirective | ESTreeStatement]):
    pass


@dataclasses.dataclass(slots=True)
class ESTreeReturnStatement(ESTreeStatement):
    argument: ESTreeExpression | None


@dataclasses.dataclass(slots=True)
class ESTreeLabeledStatement(ESTreeStatement):
    label: ESTreeIdentifier
    body: ESTreeStatement


@dataclasses.dataclass(slots=True)
class ESTreeBreakStatement(ESTreeStatement):
    label: ESTreeIdentifier | None


@dataclasses.dataclass(slots=True)
class ESTreeContinueStatement(ESTreeStatement):
    label: ESTreeIdentifier | None


@dataclasses.dataclass(slots=True)
class ESTreeIfStatement(ESTreeStatement):
    test: ESTreeExpression
    consequent: ESTreeStatement
    alternate: ESTreeStatement | None


@dataclasses.dataclass(slots=True)
class ESTreeSwitchCase(ESTreeNode):
    test: ESTreeExpression | None
    consequent: Sequence[ESTreeStatement]


@dataclasses.dataclass(slots=True)
class ESTreeSwitchStatement(ESTreeStatement):
    discriminant: ESTreeExpression
    cases: Sequence[ESTreeSwitchCase]


@dataclasses.dataclass(slots=True)
class ESTreeThrowStatement(ESTreeStatement):
    argument: ESTreeExpression


@dataclasses.dataclass(slots=True)
class ESTreeCatchClause(ESTreeNode):
    param: ESTreePattern | None
    body: ESTreeBlockStatement


@dataclasses.dataclass(slots=True)
class ESTreeTryStatement(ESTreeStatement):
    block: ESTreeBlockStatement
    handler: ESTreeCatchClause | None
    finalizer: ESTreeBlockStatement | None


@dataclasses.dataclass(slots=True)
class ESTreeWhileStatement(ESTreeStatement):
    test: ESTreeExpression
    body: ESTreeStatement


@dataclasses.dataclass(slots=True)
class ESTreeDoWhileStatement(ESTreeStatement):
    body: ESTreeStatement
    test: ESTreeExpression


@dataclasses.dataclass(slots=True)
class ESTreeForStatement(ESTreeStatement):
    init: "ESTreeVariableDeclaration | ESTreeExpression | None"
    test: ESTreeExpression | None
    update: ESTreeExpression | None
    body: ESTreeStatement


@dataclasses.dataclass(slots=True)
class ESTreeForInStatement(ESTreeStatement):
    left: "ESTreeVariableDeclaration | ESTreeExpression"
    right: ESTreeExpression
    body: ESTreeStatement


@dataclasses.dataclass(slots=True)
class ESTreeDeclaration(ESTreeStatement): ...


@dataclasses.dataclass(slots=True)
class ESTreeFunctionDeclaration(ESTreeFunction[ESTreeIdentifier], ESTreeDeclaration): ...


@dataclasses.dataclass(slots=True)
class ESTreeVariableDeclarator(ESTreeNode):
    id: ESTreePattern
    init: ESTreeExpression | None


@dataclasses.dataclass(slots=True)
class ESTreeVariableDeclaration(ESTreeDeclaration):
    declarations: Sequence[ESTreeVariableDeclarator]
    kind: Literal["var"]


##
## Expressions
##


@dataclasses.dataclass(slots=True)
class ESTreeThisExpression(ESTreeExpression): ...


@dataclasses.dataclass(slots=True)
class ESTreeArrayExpression(ESTreeExpression):
    elements: Sequence[ESTreeExpression | None]


@dataclasses.dataclass(slots=True)
class ESTreeObjectProperty(ESTreeNode):
    key: ESTreeLiteral | ESTreeIdentifier
    value: ESTreeExpression
    kind: Literal["init", "get", "set"]


@dataclasses.dataclass(slots=True)
class ESTreeObjectExpression(ESTreeExpression):
    properties: Sequence[ESTreeObjectProperty]


@dataclasses.dataclass(slots=True)
class ESTreeFunctionExpression(ESTreeFunction[ESTreeIdentifier | None], ESTreeExpression): ...


ESTreeUnaryOperator = Literal[
    "-",
    "+",
    "!",
    "~",
    "typeof",
    "void",
    "delete",
]


@dataclasses.dataclass(slots=True)
class ESTreeUnaryExpression(ESTreeExpression):
    operator: ESTreeUnaryOperator
    prefix: bool
    argument: ESTreeExpression


ESTreeUpdateOperator = Literal[
    "++",
    "--",
]


@dataclasses.dataclass(slots=True)
class ESTreeUpdateExpression(ESTreeExpression):
    operator: ESTreeUpdateOperator
    argument: ESTreeExpression
    prefix: bool


ESTreeBinaryOperator = Literal[
    "==",
    "!=",
    "===",
    "!==",
    "<",
    "<=",
    ">",
    ">=",
    "<<",
    ">>",
    ">>>",
    "+",
    "-",
    "*",
    "/",
    "%",
    "^",
    "&",
    "in",
    "instanceof",
]


@dataclasses.dataclass(slots=True)
class ESTreeBinaryExpression(ESTreeExpression):
    operator: ESTreeBinaryOperator
    left: ESTreeExpression
    right: ESTreeExpression


ESTreeLogicalOperator = Literal[
    "||",
    "&&",
    "??",
]


@dataclasses.dataclass(slots=True)
class ESTreeLogicalExpression(ESTreeExpression):
    operator: ESTreeLogicalOperator
    left: ESTreeExpression
    right: ESTreeExpression


@dataclasses.dataclass(slots=True)
class ESTreeMemberExpression(ESTreeExpression):
    object: ESTreeExpression
    property: ESTreeExpression
    computed: bool


@dataclasses.dataclass(slots=True)
class ESTreeAssignmentExpression(ESTreeExpression):
    left: ESTreeIdentifier | ESTreeMemberExpression
    right: ESTreeExpression
    operator: Literal["="] = "="


@dataclasses.dataclass(slots=True)
class ESTreeConditionalExpression(ESTreeExpression):
    test: ESTreeExpression
    alternate: ESTreeExpression
    consequent: ESTreeExpression


@dataclasses.dataclass(slots=True)
class ESTreeCallExpression(ESTreeExpression):
    callee: ESTreeExpression
    arguments: Sequence[ESTreeExpression]


@dataclasses.dataclass(slots=True)
class ESTreeNewExpression(ESTreeExpression):
    callee: ESTreeExpression
    arguments: Sequence[ESTreeExpression]


@dataclasses.dataclass(slots=True)
class ESTreeSequenceExpression(ESTreeExpression):
    expressions: Sequence[ESTreeExpression]
