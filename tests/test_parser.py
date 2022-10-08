import pytest
from jlox.expression import (
    AssignExpr,
    BinaryExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
    VariableExpr,
)
from jlox.parser import Parser
from jlox.statement import ExpressionStmt, PrintStmt, VarStmt, BlockStmt
from jlox.tokens import Token, TokenType

TT = TokenType


def str_token(val: str, tt: TT | None = None) -> Token:
    return Token(tt or TT.STRING, f'"{val}"', val, 1)


def float_token(val: float) -> Token:
    return Token(TT.NUMBER, str(val), val, 1)


def id_token(name: str) -> Token:
    return Token(TT.IDENTIFIER, name, None, 1)


def token(tt: TT, lexeme: str | None = None) -> Token:
    return Token(tt, lexeme or tt.value, None, 1)


def test_var_declaration():
    name = id_token("some_var")
    tokens = [
        Token(TokenType.VAR, "var", None, 1),
        name,
        Token(TokenType.EQUAL, "=", None, 1),
        Token(TokenType.NUMBER, "5", 5, 1),
        Token(TokenType.SEMICOLON, ";", None, 1),
        Token(TokenType.EOF, "", None, 1),
    ]

    p = Parser(tokens)

    [statement] = p.parse()

    assert isinstance(statement, VarStmt)
    assert statement.name == name
    assert statement.initializer == LiteralExpr(5)


@pytest.mark.parametrize(
    ["tokens", "exp_expr"],
    [
        (
            [str_token("hello world")],
            LiteralExpr("hello world"),
        ),
        (
            [token(TT.MINUS, "-"), float_token(3)],
            UnaryExpr(Token(TokenType.MINUS, "-", None, 1), LiteralExpr(3)),
        ),
    ],
)
def test_print_statement(tokens: list[Token], exp_expr: Expr):
    tokens = [
        Token(TokenType.PRINT, "print", None, 1),
        *tokens,
        Token(TokenType.SEMICOLON, ";", None, 1),
        Token(TokenType.EOF, "", None, 1),
    ]

    p = Parser(tokens)

    [statement] = p.parse()

    assert isinstance(statement, PrintStmt)
    assert statement.expression == exp_expr


@pytest.mark.parametrize(
    ["expr_tokens", "exp_expr"],
    [
        (
            [
                token(TT.LEFT_PAREN),
                float_token(3),
                token(TT.PLUS),
                float_token(7),
                token(TT.RIGHT_PAREN),
            ],
            GroupingExpr(BinaryExpr(LiteralExpr(3), token(TT.PLUS), LiteralExpr(7))),
        ),
        (
            [
                id_token("some_var"),
                token(TT.EQUAL),
                token(TT.MINUS),
                float_token(1),
                token(TT.SLASH),
                float_token(0.5),
            ],
            AssignExpr(
                id_token("some_var"),
                BinaryExpr(
                    UnaryExpr(token(TT.MINUS), LiteralExpr(1)),
                    token(TT.SLASH),
                    LiteralExpr(0.5),
                ),
            ),
        ),
    ],
)
def test_expression_statement(expr_tokens: list[Token], exp_expr: Expr):
    tokens = [
        *expr_tokens,
        Token(TokenType.SEMICOLON, ";", None, 1),
        Token(TokenType.EOF, "", None, 1),
    ]

    p = Parser(tokens)

    [statement] = p.parse()

    assert isinstance(statement, ExpressionStmt)
    assert statement.expression == exp_expr


# def test_block_statement(block_tokens: list[Token], exp_block_statments: list[Stmt]):
def test_block_statement():
    tokens = [
        Token(TokenType.LEFT_BRACE, "{", None, 1),
        Token(TokenType.NUMBER, "5", 5, 1),
        Token(TokenType.PLUS, "+", None, 1),
        Token(TokenType.NUMBER, "10", 10, 1),
        Token(TokenType.SEMICOLON, ";", None, 1),
        Token(TokenType.VAR, "var", None, 1),
        Token(TokenType.IDENTIFIER, "some_var", None, 1),
        Token(TokenType.EQUAL, "=", None, 1),
        Token(TokenType.NUMBER, "2", 2.0, 1),
        Token(TokenType.SEMICOLON, ";", None, 1),
        Token(TokenType.RIGHT_BRACE, "}", None, 1),
        Token(TokenType.EOF, "", None, 1),
    ]

    p = Parser(tokens)

    [statement] = p.parse()

    assert isinstance(statement, BlockStmt)
    assert statement.statements == [
        ExpressionStmt(
            BinaryExpr(
                LiteralExpr(5.0), Token(TokenType.PLUS, "+", None, 1), LiteralExpr(10.0)
            )
        ),
        VarStmt(Token(TokenType.IDENTIFIER, "some_var", None, 1), LiteralExpr(2.0)),
    ]


def test_print_assignment():
    tokens = [
        Token(TokenType.PRINT, "print", None, 1),
        Token(TokenType.IDENTIFIER, "some_var", None, 1),
        Token(TokenType.EQUAL, "=", None, 1),
        Token(TokenType.NUMBER, "3", 3, 1),
        Token(TokenType.SEMICOLON, ";", None, 1),
        Token(TokenType.EOF, "", None, 1),
    ]

    p = Parser(tokens)

    [statement] = p.parse()

    assert isinstance(statement, PrintStmt)
    assert isinstance(statement.expression, AssignExpr)
    assert statement.expression.name == Token(TokenType.IDENTIFIER, "some_var", None, 1)
    assert statement.expression.value == LiteralExpr(3)
