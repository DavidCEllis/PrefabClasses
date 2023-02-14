from ..exceptions import LivePrefabError as LivePrefabError
from ..sentinels import NOTHING as NOTHING
import typing
from _collections_abc import Callable

class Attribute:
    COMPILED: bool
    PREFAB_FIELDS: list[str]
    __match_args__: tuple[str, ...]
    default: typing.Any
    default_factory: Callable[[], typing.Any]
    init: bool
    repr: bool
    kw_only: bool
    exclude_field: bool
    _type: str | type
    def __init__(
        self,
        default=...,
        default_factory=...,
        init: bool = ...,
        repr: bool = ...,
        kw_only: bool = ...,
        exclude_field: bool = ...,
    ) -> None: ...
    @staticmethod
    def __prefab_pre_init__(init, default, default_factory, kw_only) -> None: ...
