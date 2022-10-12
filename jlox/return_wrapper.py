from typing import Any


class ReturnWrapper(Exception):
    value: Any | None

    def __init__(self, value: Any | None) -> None:
        super().__init__()

        self.value = value
