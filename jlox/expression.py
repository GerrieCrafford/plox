from dataclasses import dataclass
from typing import Protocol, TypeVar
from jlox.tokens import Token

T = TypeVar("T", covariant=True)


class ExprVisitor(Protocol[T]):
    def visitBinaryExpr(self, expr: "BinaryExpr") -> T:
        ...

    def visitGroupingExpr(self, expr: "GroupingExpr") -> T:
        ...

    def visitLiteralExpr(self, expr: "LiteralExpr") -> T:
        ...

    def visitUnaryExpr(self, expr: "UnaryExpr") -> T:
        ...

    def visitAssignExpr(self, expr: "AssignExpr") -> T:
        ...

    def visitVariableExpr(self, expr: "VariableExpr") -> T:
        ...

    def visitLogicalExpr(self, expr: "LogicalExpr") -> T:
        ...


V = TypeVar("V")


class Expr(Protocol):
    def accept(self, visitor: ExprVisitor[V]) -> V:
        ...


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitBinaryExpr(self)


@dataclass
class GroupingExpr(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitGroupingExpr(self)


@dataclass
class LiteralExpr(Expr):
    value: str | float | None

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitLiteralExpr(self)


@dataclass
class UnaryExpr(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitUnaryExpr(self)


@dataclass
class AssignExpr(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitAssignExpr(self)


@dataclass
class VariableExpr(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitVariableExpr(self)


@dataclass
class LogicalExpr(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitLogicalExpr(self)
