import typing
from collections.abc import Callable

def autogen(
        func: Callable[[type], str],
        globs: dict[str, typing.Any] | None = ...
) -> type: ...
