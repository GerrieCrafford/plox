from dataclasses import dataclass
from typing import Any
from jlox.tokens import Token, TokenType


@dataclass
class LexingError:
    line: int
    msg: str


def is_digit(char: str) -> bool:
    return char in [str(x) for x in range(10)]


def is_alpha(char: str) -> bool:
    return char.isalpha() or char == "_"


def is_alpha_numeric(char: str) -> bool:
    return is_digit(char) or is_alpha(char)


class Scanner:
    def __init__(self, source: str) -> None:
        self._source = source
        self._tokens: list[Token] = []

        self._line = 1
        self._current = 0
        self._start = 0

        self._errors: list[LexingError] = []

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self._start = self._current
            self._scan_token()

        self._tokens.append(Token(TokenType.EOF, "", None, self._line))

        return self._tokens

    def _scan_token(self) -> None:
        c = self._advance()

        match c:
            case TokenType.LEFT_PAREN.value:
                self._add_token(TokenType.LEFT_PAREN)
            case TokenType.RIGHT_PAREN.value:
                self._add_token(TokenType.RIGHT_PAREN)
            case TokenType.LEFT_BRACE.value:
                self._add_token(TokenType.LEFT_BRACE)
            case TokenType.RIGHT_BRACE.value:
                self._add_token(TokenType.RIGHT_BRACE)
            case TokenType.COMMA.value:
                self._add_token(TokenType.COMMA)
            case TokenType.DOT.value:
                self._add_token(TokenType.DOT)
            case TokenType.MINUS.value:
                self._add_token(TokenType.MINUS)
            case TokenType.PLUS.value:
                self._add_token(TokenType.PLUS)
            case TokenType.SEMICOLON.value:
                self._add_token(TokenType.SEMICOLON)
            case TokenType.STAR.value:
                self._add_token(TokenType.STAR)
            case TokenType.BANG.value:
                self._add_token(
                    TokenType.BANG_EQUAL
                    if self._match(TokenType.EQUAL.value)
                    else TokenType.BANG
                )
            case TokenType.EQUAL.value:
                self._add_token(
                    TokenType.EQUAL_EQUAL
                    if self._match(TokenType.EQUAL.value)
                    else TokenType.EQUAL
                )
            case TokenType.LESS.value:
                self._add_token(
                    TokenType.LESS_EQUAL
                    if self._match(TokenType.EQUAL.value)
                    else TokenType.LESS
                )
            case TokenType.GREATER.value:
                self._add_token(
                    TokenType.GREATER_EQUAL
                    if self._match(TokenType.EQUAL.value)
                    else TokenType.GREATER
                )
            case TokenType.SLASH.value:
                if self._match(TokenType.SLASH.value):
                    # Comment goes to EoL
                    while self._peek() != "\n" and not self._is_at_end():
                        self._advance()
                elif self._match(TokenType.STAR.value):
                    # Block comment goes to */
                    while (self._peek(), self._peek_next()) != ('*', '/') and not self._is_at_end():
                        if self._peek() == '\n':
                            self._line += 1
                        self._advance()
                    
                    if not self._is_at_end():
                        # Consume * and /
                        self._advance()
                        self._advance()
                else:
                    self._add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self._line += 1
            case TokenType.STRING.value:
                self._string()
            case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                self._number()
            case char if is_alpha(char):
                self._identifier()
            case _:
                self._error(self._line, "Invalid character")

    def _add_token(self, t: TokenType, data: Any | None = None) -> None:
        text = self._source[self._start : self._current]
        self._tokens.append(Token(t, text, data, self._line))

    def _advance(self) -> str:
        c = self._source[self._current]
        self._current += 1
        return c

    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self._source[self._current] != expected:
            return False

        self._current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"

        return self._source[self._current]

    def _peek_next(self) -> str:
        if self._current + 1 >= len(self._source):
            return "\0"

        return self._source[self._current + 1]

    def _string(self):
        while self._peek() != TokenType.STRING.value and not self._is_at_end():
            if self._peek() == "\n":
                self._line += 1

            self._advance()

        if self._is_at_end():
            self._error(self._line, "Unterminated string")

        # Closing "
        self._advance()

        val = self._source[self._start + 1 : self._current - 1]
        self._add_token(TokenType.STRING, val)

    def _number(self):
        while is_digit(self._peek()):
            self._advance()

        if self._peek() == "." and is_digit(self._peek_next()):
            # Consume the "."
            self._advance()

            while is_digit(self._peek()):
                self._advance()

        self._add_token(
            TokenType.NUMBER, float(self._source[self._start : self._current])
        )

    def _identifier(self):
        while is_alpha_numeric(self._peek()):
            self._advance()

        text = self._source[self._start : self._current]
        try:
            self._add_token(TokenType(text))
        except:
            self._add_token(TokenType.IDENTIFIER, text)

    def _error(self, line: int, msg: str):
        self._errors.append(LexingError(line, msg))
