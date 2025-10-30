import dataclasses
from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Union


class IRBinaryOperator(str, Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="


class IRExpr: ...


@dataclasses.dataclass(frozen=True)
class IRLiteralNumberExpr(IRExpr):
    value: Union[int, float]


@dataclasses.dataclass(frozen=True)
class IRLiteralBooleanExpr(IRExpr):
    value: bool


@dataclasses.dataclass(frozen=True)
class IRLiteralStringExpr(IRExpr):
    value: str


@dataclasses.dataclass(frozen=True)
class IRLiteralArrayExpr(IRExpr):
    elements: Sequence[IRExpr]


@dataclasses.dataclass(frozen=True)
class IRLiteralRecordExpr(IRExpr):
    fields: Mapping[str, IRExpr]


@dataclasses.dataclass(frozen=True)
class IRBinaryOpExpr(IRExpr):
    operator: IRBinaryOperator
    left: IRExpr
    right: IRExpr


@dataclasses.dataclass(frozen=True)
class IRIdentifierExpr(IRExpr):
    name: str


@dataclasses.dataclass(frozen=True)
class IRCallExpr(IRExpr):
    function: Union[str, IRExpr]
    args: list[IRExpr]


@dataclasses.dataclass(frozen=True)
class IRIndexAccessExpr(IRExpr):
    target: IRExpr
    index: IRExpr


@dataclasses.dataclass(frozen=True)
class IRPropertyAccessExpr(IRExpr):
    target: IRExpr
    property: str


@dataclasses.dataclass(frozen=True)
class IRMethodCallExpr(IRExpr):
    target: IRExpr
    method: str
    args: list[IRExpr]


@dataclasses.dataclass(frozen=True)
class IRThisExpr(IRExpr):
    """Represents 'this' keyword in JavaScript."""

    pass


@dataclasses.dataclass(frozen=True)
class IRNewExpr(IRExpr):
    """Represents 'new ClassName(args)' expression."""

    class_name: str
    args: list[IRExpr]


class IRStmt: ...


@dataclasses.dataclass(frozen=True)
class IRLetStmt(IRStmt):
    name: str
    value: IRExpr


@dataclasses.dataclass(frozen=True)
class IRAssignStmt(IRStmt):
    name: str
    value: IRExpr


@dataclasses.dataclass(frozen=True)
class IRExprStmt(IRStmt):
    expr: IRExpr


@dataclasses.dataclass(frozen=True)
class IRReturnStmt(IRStmt):
    value: IRExpr


@dataclasses.dataclass(frozen=True)
class IRRangeStmt(IRStmt):
    var: str
    start: IRExpr
    end: IRExpr
    body: "IRBlock"


@dataclasses.dataclass(frozen=True)
class IRIfStmt(IRStmt):
    condition: IRExpr
    then_body: "IRBlock"
    else_body: "IRBlock | None" = None


@dataclasses.dataclass(frozen=True)
class IRBlock(IRStmt):
    body: list[IRStmt]

    def emit(self, stmt: IRStmt) -> None:
        self.body.append(stmt)


@dataclasses.dataclass(frozen=True)
class IRFunctionStmt(IRStmt):
    name: str
    params: list[str]
    body: IRBlock


@dataclasses.dataclass(frozen=True)
class IRPropertyAssignStmt(IRStmt):
    """Represents property assignment like 'this.x = value'."""

    target: IRExpr  # Usually IRPropertyAccessExpr
    value: IRExpr


@dataclasses.dataclass(frozen=True)
class IRMethodStmt(IRStmt):
    """Represents a method definition in a class."""

    name: str
    params: list[str]
    body: IRBlock
    is_static: bool = False
    is_getter: bool = False


@dataclasses.dataclass(frozen=True)
class IRClassStmt(IRStmt):
    """Represents a class definition."""

    name: str
    constructor_params: list[str]
    constructor_body: IRBlock
    methods: list[IRMethodStmt]
