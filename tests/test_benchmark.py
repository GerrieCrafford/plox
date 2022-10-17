from typing import Any
import pytest

from jlox.expression import (
    CallExpr,
    LiteralExpr,
    VariableExpr,
    BinaryExpr,
)
from jlox.interpreter import Interpreter
from jlox.resolver import Resolver
from jlox.scanner import Scanner
from jlox.parser import Parser
from jlox.statement import (
    ExpressionStmt,
    FunctionStmt,
    IfStmt,
    ReturnStmt,
    Stmt,
)
from jlox.tokens import Token, TokenType


@pytest.fixture
def interpreter() -> Interpreter:
    return Interpreter()


def name(n: str, line: int = 1) -> Token:
    return Token(TokenType.IDENTIFIER, n, None, line)


def right_paren():
    return Token(TokenType.RIGHT_PAREN, ")", None, 0)


lox_fib = """
fun fib(n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);
}

var res = fib(10);
assert_equal(res, 55);
"""


@pytest.mark.skip
def test_fib(interpreter: Interpreter, benchmark: Any):
    def run():
        scanner = Scanner(lox_fib)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()
        resolver = Resolver(interpreter)

        resolver.resolve(statements)
        interpreter.interpret(statements)

    benchmark(run)
