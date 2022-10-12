from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from jlox.interpreter import Interpreter

from jlox.lox_callable import LoxCallable
from jlox.statement import FunctionStmt
from jlox.environment import Environment
from jlox.return_wrapper import ReturnWrapper


class LoxFunction(LoxCallable):
    def __init__(self, declaration: FunctionStmt) -> None:
        self._declaration = declaration

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        env = Environment(interpreter.globals)

        for param, arg in zip(self._declaration.params, arguments):
            env.define(param.lexeme, arg)

        try:
            interpreter._executeBlock(self._declaration.body, env)
        except ReturnWrapper as ret:
            return ret.value
        else:
            return None

    @property
    def arity(self) -> int:
        return len(self._declaration.params)

    def __str__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"

    def __repr__(self) -> str:
        return self.__str__()
