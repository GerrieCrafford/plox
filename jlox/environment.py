from typing import Any

from jlox.tokens import Token
from jlox.errors import JloxRuntimeError


class Environment:
    def __init__(self, enclosing: "Environment" | None = None) -> None:
        self._values: dict[str, Any] = {}
        self._enclosing = enclosing

    def define(self, name: str, val: Any):
        self._values[name] = val

    def get(self, name: Token) -> Any:
        if name.lexeme in self._values:
            return self._values[name.lexeme]
        elif self._enclosing:
            return self._enclosing.get(name)

        raise JloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return
        elif self._enclosing:
            self._enclosing.assign(name, value)
            return

        raise JloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
