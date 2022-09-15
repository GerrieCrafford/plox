from dataclasses import dataclass
from typing import Protocol, TypeVar

from jlox.expression import Expr
from jlox.tokens import Token


T = TypeVar('T', covariant=True)

class StmtVisitor(Protocol[T]):
    def visitExpressionStmt(self, stmt: 'ExpressionStmt') -> T:
        ...
    
    def visitPrintStmt(self, stmt: 'PrintStmt') -> T:
        ...
    
    def visitVarStmt(self, stmt: 'VarStmt') -> T:
        ...

V = TypeVar('V')
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