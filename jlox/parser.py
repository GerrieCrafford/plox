from jlox.tokens import Token, TokenType
from jlox.expression import BinaryExpr, Expr, GroupingExpr, LiteralExpr, UnaryExpr

class JloxSyntaxError(Exception):
    def __init__(self, token: Token, msg: str):
        if token.type == TokenType.EOF:
            m = f"l.{token.line} - at end. {msg}"
        else:
            m = f"l.{token.line} - at {token.lexeme}. {msg}"

        self._token = token
        super().__init__(m)


class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._current = 0
    
    def parse(self) -> Expr | None:
        try:
            return self._expression()
        except JloxSyntaxError as e:
            print(f'! {e}')
            return None

    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self._term()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return UnaryExpr(operator, right)

        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        if self._match(TokenType.TRUE):
            return LiteralExpr(True)
        if self._match(TokenType.NIL):
            return LiteralExpr(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return GroupingExpr(expr)

        raise JloxSyntaxError(self._peek(), "Expect expression.")

    def _match(self, *args: TokenType) -> bool:
        for ttype in args:
            if self._check(ttype):
                self._advance()
                return True

        return False

    def _check(self, ttype: TokenType) -> bool:
        if self._is_at_end():
            return False

        return self._peek().type == ttype

    def _advance(self):
        if not self._is_at_end():
            self._current += 1

        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    def _consume(self, ttype: TokenType, msg: str):
        if self._check(ttype):
            return self._advance()

        raise JloxSyntaxError(self._peek(), msg)

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return

            if self._peek().type in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.IF,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return

            self._advance()
