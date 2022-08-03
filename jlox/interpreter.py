from typing import Any
from jlox.expression import BinaryExpr, Expr, ExprVisitor, GroupingExpr, LiteralExpr, UnaryExpr
from jlox.tokens import Token, TokenType

class JloxRuntimeError(Exception):
    def __init__(self, operator: Token, msg: str) -> None:
        self._operator = operator
        super().__init__(msg)

class Interpreter(ExprVisitor[Any]):
    def interpret(self, expression: Expr):
        value = self._evaluate(expression)
        print(value)

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

        match expr.operator.type:
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self._check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                elif isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                else:
                    raise JloxRuntimeError(expr.operator, 'Operands must be two numbers or two strings')
            case TokenType.GREATER:
                self._check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case _:
                return None
    
    def _evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)
    
    def _is_truthy(self, val: Any) -> bool:
        return bool(val)
    
    def _check_number_operands(self, operator: Token, *operands: Any):
        if all(isinstance(operand, float) for operand in operands):
            return
        
        if len(operands) == 1:
            raise JloxRuntimeError(operator, 'Operand must be a number.')
        else:
            raise JloxRuntimeError(operator, 'Operands must be numbers.')