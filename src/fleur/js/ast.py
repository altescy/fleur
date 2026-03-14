import dataclasses
from typing import Any, Generic, Literal

from typing_extensions import TypeVar

from fleur.types import JsonValue

ESTreeNodeTypeT = TypeVar("ESTreeNodeTypeT", bound=str, default=Any)


@dataclasses.dataclass(slots=True)
class ESTreeNode(Generic[ESTreeNodeTypeT]):
    type: ESTreeNodeTypeT


@dataclasses.dataclass(slots=True)
class ESTreePattern(ESTreeNode[ESTreeNodeTypeT]):
    pass


@dataclasses.dataclass(slots=True)
class ESTreeExpression(ESTreeNode[ESTreeNodeTypeT]):
    pass


@dataclasses.dataclass(slots=True)
class ESTreeStatement(ESTreeNode[ESTreeNodeTypeT]):
    pass


ESTreeExpressionT = TypeVar("ESTreeExpressionT", bound=ESTreeExpression[Any], default=ESTreeExpression[Any])
ESTreeStatementT = TypeVar("ESTreeStatementT", bound=ESTreeStatement[Any], default=ESTreeStatement[Any])


##
## Identifiers
##


@dataclasses.dataclass(slots=True)
class ESTreeIdentifier(ESTreePattern, ESTreeExpression[Literal["Identifier"]]):
    name: str
    type: Literal["Identifier"] = dataclasses.field(default="Identifier", init=False)


##
## Literals
##


@dataclasses.dataclass(slots=True)
class ESTreeLiteral(ESTreeExpression[Literal["Literal"]]):
    value: JsonValue
    type: Literal["Literal"] = dataclasses.field(default="Literal", init=False)


##
## Prograsm
##


@dataclasses.dataclass(slots=True)
class ESTreeProgram(ESTreeNode[Literal["Program"]]):
    body: list["ESTreeDirective | ESTreeStatement"]
    type: Literal["Program"] = dataclasses.field(default="Program", init=False)


##
## Functions
##


ESTreeFunctionIDT = TypeVar("ESTreeFunctionIDT", bound=ESTreeIdentifier | None, default=ESTreeIdentifier | None)


@dataclasses.dataclass(slots=True)
class ESTreeFunction(ESTreeExpression[ESTreeNodeTypeT], Generic[ESTreeNodeTypeT, ESTreeFunctionIDT]):
    id: ESTreeFunctionIDT
    params: list[ESTreePattern]
    body: "ESTreeFunctionBody"


##
## Statements
##


@dataclasses.dataclass(slots=True)
class ESTreeExpressionStatement(ESTreeStatement[Literal["ExpressionStatement"]], Generic[ESTreeExpressionT]):
    expression: ESTreeExpressionT
    type: Literal["ExpressionStatement"] = dataclasses.field(default="ExpressionStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeDirective(ESTreeExpressionStatement[ESTreeLiteral]):
    directive: str


@dataclasses.dataclass(slots=True)
class ESTreeBlockStatement(ESTreeStatement[Literal["BlockStatement"]], Generic[ESTreeStatementT]):
    body: list[ESTreeStatementT]
    type: Literal["BlockStatement"] = dataclasses.field(default="BlockStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeFunctionBody(ESTreeBlockStatement[ESTreeDirective | ESTreeStatement]):
    pass


@dataclasses.dataclass(slots=True)
class ESTreeReturnStatement(ESTreeStatement[Literal["ReturnStatement"]]):
    argument: ESTreeExpression | None
    type: Literal["ReturnStatement"] = dataclasses.field(default="ReturnStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeLabeledStatement(ESTreeStatement[Literal["LabeledStatement"]]):
    label: ESTreeIdentifier
    body: ESTreeStatement
    type: Literal["LabeledStatement"] = dataclasses.field(default="LabeledStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeBreakStatement(ESTreeStatement[Literal["BreakStatement"]]):
    label: ESTreeIdentifier | None
    type: Literal["BreakStatement"] = dataclasses.field(default="BreakStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeContinueStatement(ESTreeStatement[Literal["ContinueStatement"]]):
    label: ESTreeIdentifier | None
    type: Literal["ContinueStatement"] = dataclasses.field(default="ContinueStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeIfStatement(ESTreeStatement[Literal["IfStatement"]]):
    test: ESTreeExpression
    consequent: ESTreeStatement
    alternate: ESTreeStatement | None
    type: Literal["IfStatement"] = dataclasses.field(default="IfStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeSwitchCase(ESTreeNode[Literal["SwitchCase"]]):
    test: ESTreeExpression | None
    consequent: list[ESTreeStatement]
    type: Literal["SwitchCase"] = dataclasses.field(default="SwitchCase", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeSwitchStatement(ESTreeStatement[Literal["SwitchStatement"]]):
    discriminant: ESTreeExpression
    cases: list[ESTreeSwitchCase]
    type: Literal["SwitchStatement"] = dataclasses.field(default="SwitchStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeThrowStatement(ESTreeStatement[Literal["ThrowStatement"]]):
    argument: ESTreeExpression
    type: Literal["ThrowStatement"] = dataclasses.field(default="ThrowStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeCatchClause(ESTreeNode[Literal["CatchClause"]]):
    param: ESTreePattern | None
    body: ESTreeBlockStatement
    type: Literal["CatchClause"] = dataclasses.field(default="CatchClause", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeTryStatement(ESTreeStatement[Literal["TryStatement"]]):
    block: ESTreeBlockStatement
    handler: ESTreeCatchClause | None
    finalizer: ESTreeBlockStatement | None
    type: Literal["TryStatement"] = dataclasses.field(default="TryStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeWhileStatement(ESTreeStatement[Literal["WhileStatement"]]):
    test: ESTreeExpression
    body: ESTreeStatement
    type: Literal["WhileStatement"] = dataclasses.field(default="WhileStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeDoWhileStatement(ESTreeStatement[Literal["DoWhileStatement"]]):
    body: ESTreeStatement
    test: ESTreeExpression
    type: Literal["DoWhileStatement"] = dataclasses.field(default="DoWhileStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeForStatement(ESTreeStatement[Literal["ForStatement"]]):
    init: "ESTreeVariableDeclaration | ESTreeExpression | None"
    test: ESTreeExpression | None
    update: ESTreeExpression | None
    body: ESTreeStatement
    type: Literal["ForStatement"] = dataclasses.field(default="ForStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeForInStatement(ESTreeStatement[Literal["ForInStatement"]]):
    left: "ESTreeVariableDeclaration | ESTreeExpression"
    right: ESTreeExpression
    body: ESTreeStatement
    type: Literal["ForInStatement"] = dataclasses.field(default="ForInStatement", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeDeclaration(ESTreeStatement[ESTreeNodeTypeT]):
    pass


@dataclasses.dataclass(slots=True)
class ESTreeFunctionDeclaration(
    ESTreeFunction[Literal["FunctionDeclaration"], ESTreeIdentifier],
    ESTreeDeclaration[Literal["FunctionDeclaration"]],
):
    type: Literal["FunctionDeclaration"] = dataclasses.field(default="FunctionDeclaration", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeVariableDeclarator(ESTreeNode[Literal["VariableDeclarator"]]):
    id: ESTreePattern
    init: ESTreeExpression | None
    type: Literal["VariableDeclarator"] = dataclasses.field(default="VariableDeclarator", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeVariableDeclaration(ESTreeDeclaration[Literal["VariableDeclaration"]]):
    declarations: list[ESTreeVariableDeclarator]
    kind: Literal["var"]
    type: Literal["VariableDeclaration"] = dataclasses.field(default="VariableDeclaration", init=False)


##
## Expressions
##


@dataclasses.dataclass(slots=True)
class ESTreeThisExpression(ESTreeExpression[Literal["ThisExpression"]]):
    type: Literal["ThisExpression"] = dataclasses.field(default="ThisExpression", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeArrayExpression(ESTreeExpression[Literal["ArrayExpression"]]):
    elements: list[ESTreeExpression | None]
    type: Literal["ArrayExpression"] = dataclasses.field(default="ArrayExpression", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeObjectProperty(ESTreeNode[Literal["Property"]]):
    key: ESTreeLiteral | ESTreeIdentifier
    value: ESTreeExpression
    kind: Literal["init", "get", "set"]
    type: Literal["Property"] = dataclasses.field(default="Property", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeObjectExpression(ESTreeExpression[Literal["ObjectExpression"]]):
    properties: list[ESTreeObjectProperty]
    type: Literal["ObjectExpression"] = dataclasses.field(default="ObjectExpression", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeFunctionExpression(
    ESTreeFunction[Literal["FunctionExpression"], ESTreeIdentifier | None],
    ESTreeExpression[Literal["FunctionExpression"]],
):
    type: Literal["FunctionExpression"] = dataclasses.field(default="FunctionExpression", init=False)


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
class ESTreeUnaryExpression(ESTreeExpression[Literal["UnaryExpression"]]):
    operator: ESTreeUnaryOperator
    prefix: bool
    argument: ESTreeExpression
    type: Literal["UnaryExpression"] = dataclasses.field(default="UnaryExpression", init=False)


ESTreeUpdateOperator = Literal[
    "++",
    "--",
]


@dataclasses.dataclass(slots=True)
class ESTreeUpdateExpression(ESTreeExpression[Literal["UpdateExpression"]]):
    operator: ESTreeUpdateOperator
    argument: ESTreeExpression
    prefix: bool
    type: Literal["UpdateExpression"] = dataclasses.field(default="UpdateExpression", init=False)


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
class ESTreeBinaryExpression(ESTreeExpression[Literal["BinaryExpression"]]):
    operator: ESTreeBinaryOperator
    left: ESTreeExpression
    right: ESTreeExpression
    type: Literal["BinaryExpression"] = dataclasses.field(default="BinaryExpression", init=False)


ESTreeLogicalOperator = Literal[
    "||",
    "&&",
]


@dataclasses.dataclass(slots=True)
class ESTreeLogicalExpression(ESTreeExpression[Literal["LogicalExpression"]]):
    operator: ESTreeLogicalOperator
    left: ESTreeExpression
    right: ESTreeExpression
    type: Literal["LogicalExpression"] = dataclasses.field(default="LogicalExpression", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeMemberExpression(ESTreeExpression[Literal["MemberExpression"]]):
    object: ESTreeExpression
    property: ESTreeExpression
    computed: bool
    type: Literal["MemberExpression"] = dataclasses.field(default="MemberExpression", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeConditionalExpression(ESTreeExpression[Literal["ConditionalExpression"]]):
    test: ESTreeExpression
    alternate: ESTreeExpression
    consequent: ESTreeExpression
    type: Literal["ConditionalExpression"] = dataclasses.field(default="ConditionalExpression", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeCallExpression(ESTreeExpression[Literal["CallExpression"]]):
    callee: ESTreeExpression
    arguments: list[ESTreeExpression]
    type: Literal["CallExpression"] = dataclasses.field(default="CallExpression", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeNewExpression(ESTreeExpression[Literal["NewExpression"]]):
    callee: ESTreeExpression
    arguments: list[ESTreeExpression]
    type: Literal["NewExpression"] = dataclasses.field(default="NewExpression", init=False)


@dataclasses.dataclass(slots=True)
class ESTreeSequenceExpression(ESTreeExpression[Literal["SequenceExpression"]]):
    expressions: list[ESTreeExpression]
    type: Literal["SequenceExpression"] = dataclasses.field(default="SequenceExpression", init=False)
