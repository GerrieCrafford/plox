from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from jlox.lox_class import LoxClass

from jlox.tokens import Token
from jlox.errors import JloxRuntimeError


class LoxInstance:
    def __init__(self, kind: "LoxClass") -> None:
        self._kind = kind
        self._fields: dict[str, Any] = {}

    def get(self, name: Token) -> Any:
        if name.lexeme in self._fields:
            return self._fields[name.lexeme]

        method = self._kind.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise JloxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self._fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"{self._kind.name} instance"

    def __repr__(self) -> str:
        return f"<instance {self._kind.name}>"
