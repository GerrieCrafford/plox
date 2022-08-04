from dataclasses import dataclass
from typing import Protocol, TypeVar

from jlox.expression import Expr


T = TypeVar('T', covariant=True)

class StmtVisitor(Protocol[T]):
    def visitExpressionStmt(self, stmt: 'ExpressionStmt') -> T:
        ...
    
    def visitPrintStmt(self, stmt: 'PrintStmt') -> T:
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
