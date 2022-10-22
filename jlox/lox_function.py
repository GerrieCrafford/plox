from typing import Any, TYPE_CHECKING
from enum import Enum

from jlox.lox_instance import LoxInstance
from jlox.tokens import Token, TokenType

if TYPE_CHECKING:
    from jlox.interpreter import Interpreter

from jlox.lox_callable import LoxCallable
from jlox.statement import FunctionStmt
from jlox.environment import Environment
from jlox.exception_wrappers import ReturnWrapper


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1
    METHOD = 2
    INITIALIZER = 3


def this_token():
    return Token(TokenType.THIS, "this", None, 0)


class LoxFunction(LoxCallable):
    def __init__(
        self,
        declaration: FunctionStmt,
        closure: Environment,
        is_initializer: bool = False,
    ) -> None:
        self._declaration = declaration
        self._closure = closure
        self._is_initializer = is_initializer

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        env = Environment(self._closure)

        for param, arg in zip(self._declaration.params, arguments):
            env.define(param.lexeme, arg)

        try:
            interpreter._executeBlock(self._declaration.body, env)
        except ReturnWrapper as ret:
            if self._is_initializer:
                return self._closure.get_at(0, this_token())
            return ret.value

        if self._is_initializer:
            return self._closure.get_at(0, this_token())

        return None

    def bind(self, instance: LoxInstance) -> "LoxFunction":
        env = Environment(self._closure)
        env.define("this", instance)
        return LoxFunction(self._declaration, env, self._is_initializer)

    @property
    def arity(self) -> int:
        return len(self._declaration.params)

    def __str__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"

    def __repr__(self) -> str:
        return self.__str__()
