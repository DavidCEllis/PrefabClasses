# DO NOT MANUALLY EDIT THIS FILE
# THIS MODULE IS AUTOMATICALLY GENERATED FROM _attribute_template.py
# BY regenerate_attribute.py
# MODIFY THOSE MODULES AND RERUN regenerate_attribute.py

from ..sentinels import NOTHING
from ..exceptions import LivePrefabError

class Attribute:
    __slots__ = ('default', 'default_factory', 'init', 'repr', 'compare', 'kw_only', 'exclude_field', '_type')
    __match_args__ = ('default', 'default_factory', 'init', 'repr', 'compare', 'kw_only', 'exclude_field', '_type')
    init: bool
    repr: bool
    compare: bool
    kw_only: bool
    exclude_field: bool

    def __init__(self, *, default=NOTHING, default_factory=NOTHING, init: bool=True, repr: bool=True, compare: bool=True, kw_only: bool=False, exclude_field: bool=False):
        self.__prefab_pre_init__(init=init, default=default, default_factory=default_factory, kw_only=kw_only)
        self.default = default
        self.default_factory = default_factory
        self.init = init
        self.repr = repr
        self.compare = compare
        self.kw_only = kw_only
        self.exclude_field = exclude_field
        self._type = NOTHING

    def __repr__(self):
        return f'{type(self).__qualname__}(default={self.default!r}, default_factory={self.default_factory!r}, init={self.init!r}, repr={self.repr!r}, compare={self.compare!r}, kw_only={self.kw_only!r}, exclude_field={self.exclude_field!r})'

    def __eq__(self, other):
        return (self.default, self.default_factory, self.init, self.repr, self.compare, self.kw_only, self.exclude_field) == (other.default, other.default_factory, other.init, other.repr, other.compare, other.kw_only, other.exclude_field) if self.__class__ == other.__class__ else NotImplemented

    @staticmethod
    def __prefab_pre_init__(init, default, default_factory, kw_only):
        if kw_only and (not init):
            raise LivePrefabError('Attribute cannot be keyword only if it is not in init.')
        if default is not NOTHING and default_factory is not NOTHING:
            raise LivePrefabError('Cannot define both a default value and a default factory.')