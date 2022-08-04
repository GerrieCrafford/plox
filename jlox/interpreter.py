from typing import Any
from jlox.expression import (
    BinaryExpr,
    Expr,
    ExprVisitor,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
)
from jlox.tokens import Token, TokenType
from jlox.statement import Stmt, StmtVisitor, ExpressionStmt, PrintStmt


class JloxRuntimeError(Exception):
    def __init__(self, operator: Token, msg: str) -> None:
        self._operator = operator
        super().__init__(msg)


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
    def interpret(self, statements: list[Stmt]):
        for stmt in statements:
            self._execute(stmt)

    def visitLiteralExpr(self, expr: LiteralExpr) -> Any:
        return expr.value

    def visitGroupingExpr(self, expr: GroupingExpr) -> Any:
        return self._evaluate(expr.expression)

    def visitUnaryExpr(self, expr: UnaryExpr) -> Any:
        right = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not self._is_truthy(right)
            case _:
                return None

    def visitBinaryExpr(self, expr: BinaryExpr) -> Any:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match (expr.operator.type, left, right):
            case TokenType.MINUS, float(l), float(r):
                return l - r
            case TokenType.SLASH, float(l), float(r):
                return l / r
            case TokenType.STAR, float(l), float(r):
                return l * r
            case TokenType.PLUS, float(l), float(r):
                return l + r
            case TokenType.PLUS, str(l), str(r):
                return l + r
            case TokenType.GREATER, float(l), float(r):
                return l > r
            case TokenType.GREATER_EQUAL, float(l), float(r):
                return l >= r
            case TokenType.LESS, float(l), float(r):
                return l < r
            case TokenType.LESS_EQUAL, float(l), float(r):
                return l <= r
            case TokenType.BANG_EQUAL, l, r:
                return l != r
            case TokenType.EQUAL_EQUAL, l, r:
                return l == r
            case tt, _, _:
                if tt in [
                    TokenType.MINUS,
                    TokenType.SLASH,
                    TokenType.STAR,
                    TokenType.GREATER,
                    TokenType.GREATER_EQUAL,
                    TokenType.LESS,
                    TokenType.LESS_EQUAL,
                ]:
                    raise JloxRuntimeError(expr.operator, 'Operands must be two numbers')
                
                if tt == TokenType.PLUS:
                    raise JloxRuntimeError(expr.operator, 'Operands must be two numbers or two strings')
                
                return None
            case _:
                return None

    def visitExpressionStmt(self, stmt: "ExpressionStmt") -> None:
        self._evaluate(stmt.expression)

    def visitPrintStmt(self, stmt: "PrintStmt") -> None:
        value = self._evaluate(stmt.expression)
        print(value)

    def _evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def _execute(self, stmt: Stmt):
        stmt.accept(self)

    def _is_truthy(self, val: Any) -> bool:
        return bool(val)

    def _check_number_operands(self, operator: Token, *operands: Any):
        if all(isinstance(operand, float) for operand in operands):
            return

        if len(operands) == 1:
            raise JloxRuntimeError(operator, "Operand must be a number.")
        else:
            raise JloxRuntimeError(operator, "Operands must be numbers.")
