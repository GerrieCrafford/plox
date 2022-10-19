from jlox.tokens import Token, TokenType


class JloxSyntaxError(Exception):
    def __init__(self, token: Token, msg: str):
        if token.type == TokenType.EOF:
            m = f"l.{token.line} - at end. {msg}"
        else:
            m = f"l.{token.line} - at {token.lexeme}. {msg}"

        self.token = token
        super().__init__(m)


class JloxRuntimeError(Exception):
    def __init__(self, operator: Token, msg: str) -> None:
        self.operator = operator
        super().__init__(msg)
