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

_GraineTypeS_co = TypeVar("_GraineTypeS_co", bound=GraineType, covariant=True)
_GraineTypeT_co = TypeVar("_GraineTypeT_co", bound=GraineType, covariant=True, default=GraineType)


class GraineASTNode: ...


class GraineASTExpr(GraineASTNode, Generic[_GraineTypeT_co]): ...


class GraineASTStmt(GraineASTNode): ...


class GraineUndefinedNode(GraineASTExpr[GraineUndefinedType]): ...


@dataclasses.dataclass
class GraineBooleanNode(GraineASTExpr[GraineBooleanType]):
    value: bool


@dataclasses.dataclass
class GraineNumberNode(GraineASTExpr[GraineNumberType]):
    value: float


@dataclasses.dataclass
class GraineStringNode(GraineASTExpr[GraineStringType]):
    value: str


@dataclasses.dataclass
class GraineArrayNode(GraineASTExpr[GraineArrayType], Generic[_GraineTypeT_co]):
    elements: list[GraineASTExpr[_GraineTypeT_co]] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GraineRecordNode(GraineASTExpr[GraineRecordType], Generic[_GraineTypeT_co]):
    fields: dict[str, GraineASTExpr[_GraineTypeT_co]] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class GraineBinaryOpNode(GraineASTExpr[_GraineTypeT_co]):
    op: str
    left: GraineASTExpr
    right: GraineASTExpr


@dataclasses.dataclass
class GraineIdentifierNode(GraineASTExpr[_GraineTypeT_co]):
    name: str


@dataclasses.dataclass
class GraineCallNode(GraineASTExpr[_GraineTypeT_co]):
    function: GraineASTExpr
    arguments: list[GraineASTExpr] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GrainePropertyAccessNode(GraineASTExpr[_GraineTypeT_co]):
    property_name: str
    receiver: GraineASTExpr


@dataclasses.dataclass
class GraineIndexAccessNode(GraineASTExpr[_GraineTypeT_co]):
    index: GraineASTExpr[GraineNumberType]
    receiver: GraineASTExpr


@dataclasses.dataclass
class GraineConditionalNode(GraineASTExpr[Union[_GraineTypeS_co, _GraineTypeT_co, GraineUndefinedType]]):
    condition: GraineASTExpr[GraineBooleanLikeType]
    then_branch: GraineASTExpr[_GraineTypeS_co]
    else_branch: Optional[GraineASTExpr[_GraineTypeT_co]] = None


@dataclasses.dataclass
class GraineConstructionNode(GraineASTExpr[GraineClassType]):
    class_name: str
    arguments: list[GraineASTExpr] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GraineLetNode(GraineASTStmt):
    identifier: GraineIdentifierNode
    value: GraineASTExpr


@dataclasses.dataclass
class GraineAssignNode(GraineASTStmt):
    identifier: GraineASTExpr
    value: GraineASTExpr


@dataclasses.dataclass
class GraineReturnNode(GraineASTStmt):
    value: GraineASTExpr


@dataclasses.dataclass
class GraineBlockNode(GraineASTStmt):
    statements: list[GraineASTStmt] = dataclasses.field(default_factory=list)

    def emit(self, *stmt: GraineASTStmt) -> None:
        self.statements.extend(stmt)

    def new_identifier(self, prefix: str = "_v_") -> GraineIdentifierNode:
        name = f"{prefix}{len(self.statements)}"
        return GraineIdentifierNode(name=name)


@dataclasses.dataclass
class GraineFunctionNode(GraineASTStmt):
    name: str
    parameters: list["GraineIdentifierNode"] = dataclasses.field(default_factory=list)
    body: GraineBlockNode = dataclasses.field(default_factory=GraineBlockNode)


@dataclasses.dataclass
class GraineMethodNode(GraineASTStmt):
    name: str
    function: GraineFunctionNode
    accessor: Optional[Literal["get", "set"]] = None


@dataclasses.dataclass
class GraineClassNode(GraineASTStmt):
    name: str
    constructor: Optional[GraineFunctionNode] = None
    methods: list[GraineMethodNode] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class GraineForOfNode(GraineASTStmt):
    variable: GraineIdentifierNode
    iterator: GraineASTExpr[GraineArrayType]
    body: GraineBlockNode = dataclasses.field(default_factory=GraineBlockNode)


@dataclasses.dataclass
class GraineIfNode(GraineASTStmt):
    condition: GraineASTExpr[GraineBooleanLikeType]
    then_branch: GraineBlockNode = dataclasses.field(default_factory=GraineBlockNode)
    else_branch: Optional[GraineBlockNode] = None
