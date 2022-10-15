import pytest

from jlox.expression import CallExpr, LiteralExpr, VariableExpr, Expr
from jlox.interpreter import Interpreter
from jlox.resolver import Resolver
from jlox.statement import (
    BlockStmt,
    ExpressionStmt,
    FunctionStmt,
    ReturnStmt,
    Stmt,
    VarStmt,
)
from jlox.tokens import Token, TokenType


@pytest.fixture
def interpreter() -> Interpreter:
    return Interpreter()


def name(n: str, line: int = 1) -> Token:
    return Token(TokenType.IDENTIFIER, n, None, line)


def number_expr(val: int | float) -> LiteralExpr:
    return LiteralExpr(val)


def closing_paren(line: int = 1) -> Token:
    return Token(TokenType.RIGHT_PAREN, ")", None, line)


def return_token(line: int = 1) -> Token:
    return Token(TokenType.RETURN, "return", None, line)


def lox_assert(expr1: Expr, expr2: Expr) -> ExpressionStmt:
    return ExpressionStmt(
        CallExpr(
            VariableExpr(Token(TokenType.IDENTIFIER, "assert_equal", None, 1)),
            closing_paren(),
            [expr1, expr2],
        )
    )


def test_assert_equal_works(interpreter: Interpreter):
    resolver = Resolver(interpreter)

    statements: list[Stmt] = [lox_assert(number_expr(1), number_expr(1))]
    resolver.resolve(statements)
    interpreter.interpret(statements)

    statements = [lox_assert(number_expr(1), number_expr(2))]
    with pytest.raises(AssertionError):
        interpreter.interpret(statements)


def test_closure_variable_capturing(interpreter: Interpreter):
    """
    Closure should capture variable and then keep using the same variable regardless
    of whether other variables are defined after that in the local scope.
    """
    resolver = Resolver(interpreter)

    statements: list[Stmt] = [
        VarStmt(name("a"), LiteralExpr("global")),
        BlockStmt(
            [
                FunctionStmt(
                    name("retA"),
                    [],
                    [ReturnStmt(return_token(), VariableExpr(name("a")))],
                ),
                lox_assert(
                    CallExpr(VariableExpr(name("retA")), closing_paren(), []),
                    LiteralExpr("global"),
                ),
                VarStmt(name("a"), LiteralExpr("block")),
                lox_assert(
                    CallExpr(VariableExpr(name("retA")), closing_paren(), []),
                    LiteralExpr("global"),
                ),
            ]
        ),
    ]

    resolver.resolve(statements)
    interpreter.interpret(statements)
