import dataclasses
from enum import Enum
from typing import Union


class IRBinaryOperator(str, Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"


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
class IRBinaryOpExpr(IRExpr):
    operator: IRBinaryOperator
    left: IRExpr
    right: IRExpr


@dataclasses.dataclass(frozen=True)
class IRIdentifierExpr(IRExpr):
    name: str


@dataclasses.dataclass(frozen=True)
class IRCallExpr(IRExpr):
    function: str
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
class IRBlock(IRStmt):
    body: list[IRStmt]

    def emit(self, stmt: IRStmt) -> None:
        self.body.append(stmt)


@dataclasses.dataclass(frozen=True)
class IRFunctionStmt(IRStmt):
    name: str
    params: list[str]
    body: IRBlock
