from typing import Any, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from jlox.interpreter import Interpreter

from jlox.lox_callable import LoxCallable


class ClockFunc(LoxCallable):
    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        return time.time()

    @property
    def arity(self) -> int:
        return 0
