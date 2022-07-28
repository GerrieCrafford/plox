from jlox.scanner import Scanner
from jlox.token import Token, TokenType
import pytest

TEST_VALS = [
    (
        "5 +\n7",
        [
            Token(TokenType.NUMBER, "5", 5.0, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "7", 7.0, 2),
            Token(TokenType.EOF, "", None, 2),
        ],
    ),
    (
        '(1.12 + 0.1 - 3) > 9.1 and 2 == 3 or (1 - 0.1 / 7 * 3) <= 7 and true == false;',
        [
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.NUMBER, "1.12", 1.12, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "0.1", 0.1, 1),
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "3", 3, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.GREATER, ">", None, 1),
            Token(TokenType.NUMBER, "9.1", 9.1, 1),
            Token(TokenType.AND, "and", None, 1),
            Token(TokenType.NUMBER, "2", 2, 1),
            Token(TokenType.EQUAL_EQUAL, "==", None, 1),
            Token(TokenType.NUMBER, "3", 3, 1),
            Token(TokenType.OR, "or", None, 1),
            Token(TokenType.LEFT_PAREN, "(", None, 1),
            Token(TokenType.NUMBER, "1", 1, 1),
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "0.1", 0.1, 1),
            Token(TokenType.SLASH, "/", None, 1),
            Token(TokenType.NUMBER, "7", 7, 1),
            Token(TokenType.STAR, "*", None, 1),
            Token(TokenType.NUMBER, "3", 3, 1),
            Token(TokenType.RIGHT_PAREN, ")", None, 1),
            Token(TokenType.LESS_EQUAL, "<=", None, 1),
            Token(TokenType.NUMBER, "7", 7, 1),
            Token(TokenType.AND, "and", None, 1),
            Token(TokenType.TRUE, "true", None, 1),
            Token(TokenType.EQUAL_EQUAL, "==", None, 1),
            Token(TokenType.FALSE, "false", None, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
    ),
    (
        'some_var=5.8\nother_var=some_var+1 // this is a comment\n//another comment\nreturn nil',
        [
            Token(TokenType.IDENTIFIER, "some_var", 'some_var', 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.NUMBER, "5.8", 5.8, 1),
            Token(TokenType.IDENTIFIER, "other_var", 'other_var', 2),
            Token(TokenType.EQUAL, "=", None, 2),
            Token(TokenType.IDENTIFIER, "some_var", 'some_var', 2),
            Token(TokenType.PLUS, "+", None, 2),
            Token(TokenType.NUMBER, "1", 1, 2),
            Token(TokenType.RETURN, "return", None, 4),
            Token(TokenType.NIL, "nil", None, 4),
            Token(TokenType.EOF, "", None, 4),
        ]
    ),
    (
        'some_var=/*change this value*/"test_value"',
        [
            Token(TokenType.IDENTIFIER, "some_var", 'some_var', 1),
            Token(TokenType.EQUAL, "=", None, 1),
            Token(TokenType.STRING, "test_value", 'test_value', 1),
            Token(TokenType.EOF, "", None, 1),
        ]
    )
]


@pytest.mark.parametrize(["source", "exp_tokens"], TEST_VALS)
def test_output_tokens(source: str, exp_tokens: list[Token]):
    s = Scanner(source)
    tokens = s.scan_tokens()

    assert tokens == exp_tokens
