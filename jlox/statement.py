from dataclasses import dataclass
from typing import Protocol, Sequence, TypeVar

from jlox.expression import Expr, VariableExpr
from jlox.tokens import Token


T = TypeVar("T", covariant=True)


class StmtVisitor(Protocol[T]):
    def visitExpressionStmt(self, stmt: "ExpressionStmt") -> T:
        ...

    def visitPrintStmt(self, stmt: "PrintStmt") -> T:
        ...

    def visitVarStmt(self, stmt: "VarStmt") -> T:
        ...

    def visitBlockStmt(self, stmt: "BlockStmt") -> T:
        ...

    def visitIfStmt(self, stmt: "IfStmt") -> T:
        ...

    def visitWhileStmt(self, stmt: "WhileStmt") -> T:
        ...

    def visitFunctionStmt(self, stmt: "FunctionStmt") -> T:
        ...

    def visitReturnStmt(self, stmt: "ReturnStmt") -> T:
        ...

    def visitClassStmt(self, stmt: "ClassStmt") -> T:
        ...


V = TypeVar("V")


class Stmt(Protocol):
    def accept(self, visitor: StmtVisitor[V]) -> V:
        ...


@dataclass
class ExpressionStmt(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitExpressionStmt(self)


@dataclass
class PrintStmt(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitPrintStmt(self)


@dataclass
class VarStmt(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitVarStmt(self)


@dataclass
class BlockStmt(Stmt):
    statements: Sequence[Stmt]

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitBlockStmt(self)


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitIfStmt(self)


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    loop_body: Stmt

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitWhileStmt(self)


@dataclass
class FunctionStmt(Stmt):
    name: Token
    params: list[Token]
    body: Sequence[Stmt]

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitFunctionStmt(self)


@dataclass
class ReturnStmt(Stmt):
    keyword: Token
    value: Expr | None

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitReturnStmt(self)


@dataclass
class ClassStmt(Stmt):
    name: Token
    superclass: VariableExpr | None
    methods: Sequence[FunctionStmt]

    def accept(self, visitor: StmtVisitor[V]) -> V:
        return visitor.visitClassStmt(self)
