from enum import Enum
from typing import Any, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from jlox.interpreter import Interpreter

from jlox.lox_callable import LoxCallable
from jlox.lox_instance import LoxInstance
from jlox.lox_function import LoxFunction


class ClassType(Enum):
    NONE = 0
    CLASS = 1
    SUBCLASS = 2


class LoxClass(LoxCallable):
    def __init__(
        self,
        name: str,
        superclass: Optional["LoxClass"],
        methods: dict[str, LoxFunction],
    ) -> None:
        self._name = name
        self._superclass = superclass
        self._methods = methods

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any | None:
        instance = LoxInstance(self)

        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def find_method(self, name: str) -> LoxFunction | None:
        if name in self._methods:
            return self._methods[name]

        if self._superclass:
            return self._superclass.find_method(name)

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
