from typing import Any, Union

from jlox.tokens import Token
from jlox.errors import JloxRuntimeError


class Environment:
    def __init__(self, enclosing: Union["Environment", None] = None) -> None:
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

    def get_at(self, dist: int, name: Token) -> Any:
        return self._ancestor(dist, name).get(name)

    def assign(self, name: Token, value: Any):
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return
        elif self._enclosing:
            self._enclosing.assign(name, value)
            return

        raise JloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, dist: int, name: Token, value: Any):
        self._ancestor(dist, name).assign(name, value)

    @property
    def enclosing(self) -> Union["Environment", None]:
        return self._enclosing

    def _ancestor(self, dist: int, token: Token) -> "Environment":
        env = self
        for _ in range(dist):
            if env.enclosing is None:
                raise JloxRuntimeError(
                    token,
                    "Ran out of enclosing environments before finding correct environment.",
                )

            env = env.enclosing

        return env
