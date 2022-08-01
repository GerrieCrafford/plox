from jlox.tokens import Token, TokenType
from jlox.expression import (
    Expr,
    ExprVisitor,
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
)


class AstPrinter(ExprVisitor[str]):
    def visitBinaryExpr(self, expr: BinaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: GroupingExpr) -> str:
        return self._parenthesize('group', expr.expression)

    def visitLiteralExpr(self, expr: LiteralExpr) -> str:
        return str(expr.value or 'nil')

    def visitUnaryExpr(self, expr: UnaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)
    
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        s = f"({name} "
        s += " ".join([expr.accept(self) for expr in exprs])
        s += ')'

        return s

if __name__ == '__main__':
    expression = BinaryExpr(
        UnaryExpr(
            Token(TokenType.MINUS, '-', None, 1),
            LiteralExpr(123)
        ),
        Token(TokenType.STAR, '*', None, 1),
        GroupingExpr(LiteralExpr(45.67))
    )

    ast_str = AstPrinter().print(expression)
    print(f'AST:\n{ast_str}')