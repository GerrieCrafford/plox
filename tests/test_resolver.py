import pytest
from jlox.expression import LiteralExpr

from jlox.interpreter import Interpreter
from jlox.resolver import Resolver
from jlox.statement import ReturnStmt, VarStmt, BlockStmt
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
