from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from jlox.interpreter import Interpreter


@runtime_checkable
class LoxCallable(Protocol):
    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        ...

    @property
    def arity(self) -> int:
        ...
