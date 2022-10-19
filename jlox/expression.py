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

    def visitCallExpr(self, expr: "CallExpr") -> T:
        ...

    def visitGetExpr(self, expr: "GetExpr") -> T:
        ...

    def visitSetExpr(self, expr: "SetExpr") -> T:
        ...

    def visitThisExpr(self, expr: "ThisExpr") -> T:
        ...

    def visitSuperExpr(self, expr: "SuperExpr") -> T:
        ...

    def visitCommaExpr(self, expr: "CommaExpr") -> T:
        ...

    def visitIfElseExpr(self, expr: "IfElseExpr") -> T:
        ...


V = TypeVar("V")


class Expr(Protocol):
    def accept(self, visitor: ExprVisitor[V]) -> V:
        ...

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitBinaryExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class GroupingExpr(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitGroupingExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class LiteralExpr(Expr):
    value: str | float | None

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitLiteralExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class UnaryExpr(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitUnaryExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class AssignExpr(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitAssignExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class VariableExpr(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitVariableExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class LogicalExpr(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitLogicalExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class CallExpr(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitCallExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class GetExpr(Expr):
    name: Token
    object: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitGetExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class SetExpr(Expr):
    name: Token
    object: Expr
    value: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitSetExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class ThisExpr(Expr):
    keyword: Token

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitThisExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class SuperExpr(Expr):
    keyword: Token
    method: Token

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitSuperExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class CommaExpr(Expr):
    left: Expr
    right: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitCommaExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)


@dataclass
class IfElseExpr(Expr):
    conditional: Expr
    then_expr: Expr
    else_expr: Expr

    def accept(self, visitor: ExprVisitor[V]) -> V:
        return visitor.visitIfElseExpr(self)

    def __hash__(self) -> int:
        """
        Use ID as hash because we want expressions to be globally unique
        in dicts.
        """
        return id(self)
