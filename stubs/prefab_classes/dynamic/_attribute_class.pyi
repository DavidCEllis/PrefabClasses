from ..exceptions import LivePrefabError as LivePrefabError
from ..sentinels import NOTHING as NOTHING
import typing

class Attribute:
    COMPILED: bool
    PREFAB_FIELDS: list[str]
    __match_args__: tuple[str, ...]
    default: typing.Any
    default_factory: typing.Any
    init: bool
    repr: bool
    kw_only: bool
    exclude_field: bool
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
