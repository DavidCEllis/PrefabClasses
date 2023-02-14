from ..constants import (
    CLASSVAR_NAME as CLASSVAR_NAME,
    COMPILED_FLAG as COMPILED_FLAG,
    FIELDS_ATTRIBUTE as FIELDS_ATTRIBUTE,
    POST_INIT_FUNC as POST_INIT_FUNC,
    PRE_INIT_FUNC as PRE_INIT_FUNC,
)
from ..exceptions import (
    CompiledPrefabError as CompiledPrefabError,
    LivePrefabError as LivePrefabError,
    PrefabError as PrefabError,
)
from ..sentinels import KW_ONLY as KW_ONLY, NOTHING as NOTHING
from ._attribute_class import Attribute as Attribute
from .method_generators import (
    eq_maker as eq_maker,
    frozen_delattr_maker as frozen_delattr_maker,
    frozen_setattr_maker as frozen_setattr_maker,
    init_maker as init_maker,
    iter_maker as iter_maker,
    prefab_init_maker as prefab_init_maker,
    repr_maker as repr_maker,
    repr_maker_no_eval as repr_maker_no_eval,
)

from collections.abc import Callable
from typing import dataclass_transform, overload, TypeVar

T = TypeVar("T")

SLOW_TYPING: bool

def attribute(
    *,
    default=...,
    default_factory=...,
    init: bool = ...,
    repr: bool = ...,
    kw_only: bool = ...,
    exclude_field: bool = ...,
): ...

@dataclass_transform(field_specifiers=(attribute,))
def _make_prefab(
    cls: type[T],
    *,
    init: bool = ...,
    repr: bool = ...,
    eq: bool = ...,
    iter: bool = ...,
    match_args: bool = ...,
    kw_only: bool = ...,
    frozen: bool = ...,
) -> type[T]: ...


@overload
def prefab(
    cls: None = ...,
    *,
    init: bool = ...,
    repr: bool = ...,
    eq: bool = ...,
    iter: bool = ...,
    match_args: bool = ...,
    kw_only: bool = ...,
    frozen: bool = ...,
    compile_prefab: bool = ...,
    compile_fallback: bool = ...,
    compile_plain: bool = ...,
    compile_slots: bool = ...,
) -> Callable[[type[T]], type[T]]: ...

@overload
# @dataclass_transform(field_specifiers=(attribute,))
def prefab(
    cls: type[T],
    *,
    init: bool = ...,
    repr: bool = ...,
    eq: bool = ...,
    iter: bool = ...,
    match_args: bool = ...,
    kw_only: bool = ...,
    frozen: bool = ...,
    compile_prefab: bool = ...,
    compile_fallback: bool = ...,
    compile_plain: bool = ...,
    compile_slots: bool = ...,
) -> type[T]: ...

def build_prefab(
    class_name: str,
    attributes: list[tuple[str, Attribute]],
    *,
    bases: tuple[type, ...] = ...,
    class_dict: None | dict[str, object] = ...,
    init: bool = ...,
    repr: bool = ...,
    eq: bool = ...,
    iter: bool = ...,
    match_args: bool = ...,
    kw_only: bool = ...,
    frozen: bool = ...,
) -> type: ...
