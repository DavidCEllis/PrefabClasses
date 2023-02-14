from ..constants import (
    FIELDS_ATTRIBUTE as FIELDS_ATTRIBUTE,
    POST_INIT_FUNC as POST_INIT_FUNC,
    PREFAB_INIT_FUNC as PREFAB_INIT_FUNC,
    PRE_INIT_FUNC as PRE_INIT_FUNC,
)
from ..exceptions import FrozenPrefabError as FrozenPrefabError
from ..sentinels import NOTHING as NOTHING
from .autogen import autogen as autogen

def get_init_maker(*, init_name: str = ...) -> type: ...
def get_repr_maker(will_eval: bool = ...) -> type: ...
def get_eq_maker() -> type: ...
def get_iter_maker() -> type: ...
def get_frozen_setattr_maker() -> type: ...
def get_frozen_delattr_maker() -> type: ...

init_maker: type
prefab_init_maker: type
repr_maker: type
repr_maker_no_eval: type
eq_maker: type
iter_maker: type
frozen_setattr_maker: type
frozen_delattr_maker: type
