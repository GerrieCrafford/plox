from enum import Enum
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from jlox.interpreter import Interpreter

from jlox.lox_callable import LoxCallable
from jlox.lox_instance import LoxInstance
from jlox.lox_function import LoxFunction


class ClassType(Enum):
    NONE = 0
    CLASS = 1


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict[str, LoxFunction]) -> None:
        self._name = name
        self._methods = methods

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any | None:
        instance = LoxInstance(self)

        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def find_method(self, name: str) -> LoxFunction | None:
        return self._methods.get(name, None)

    @property
    def arity(self) -> int:
        initializer = self.find_method("init")

        if initializer:
            return initializer.arity
        else:
            return 0

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"<class {self._name}>"
