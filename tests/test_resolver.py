import pytest
from jlox.expression import LiteralExpr, ThisExpr

from jlox.interpreter import Interpreter
from jlox.resolver import Resolver
from jlox.statement import (
    ClassStmt,
    FunctionStmt,
    PrintStmt,
    ReturnStmt,
    VarStmt,
    BlockStmt,
)
from jlox.tokens import Token, TokenType
from jlox.errors import JloxSyntaxError


@pytest.fixture
def resolver():
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    return resolver


def name(n: str, line: int = 1) -> Token:
    return Token(TokenType.IDENTIFIER, n, None, line)


def test_error_on_redeclare_var(resolver: Resolver):
    statements = [
        BlockStmt(
            [
                VarStmt(name("var1"), LiteralExpr(5)),
                VarStmt(name("var1"), LiteralExpr(6)),
            ]
        )
    ]

    with pytest.raises(JloxSyntaxError):
        resolver.resolve(statements)


def test_error_on_return_outside_function(resolver: Resolver):
    statements = [ReturnStmt(Token(TokenType.RETURN, "return", None, 1), None)]

    with pytest.raises(JloxSyntaxError):
        resolver.resolve(statements)


def test_error_on_return_in_init(resolver: Resolver):
    statements = [
        ClassStmt(
            name("TestClass"),
            [
                FunctionStmt(
                    name("init"),
                    [],
                    [
                        ReturnStmt(
                            Token(TokenType.RETURN, "return", None, 1), LiteralExpr(5)
                        )
                    ],
                )
            ],
        )
    ]

    with pytest.raises(JloxSyntaxError):
        resolver.resolve(statements)


def test_error_on_this_outside_method(resolver: Resolver):
    statements = [PrintStmt(ThisExpr(Token(TokenType.THIS, "this", None, 1)))]

    with pytest.raises(JloxSyntaxError):
        resolver.resolve(statements)
