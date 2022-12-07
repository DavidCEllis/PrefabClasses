# DO NOT MANUALLY EDIT THIS FILE
# THIS MODULE IS AUTOMATICALLY GENERATED FROM _attribute_template.py
# BY regenerate_attribute.py
# MODIFY THOSE MODULES AND RERUN regenerate_attribute.py

from ..sentinels import NOTHING
from ..exceptions import LivePrefabError

class Attribute:
    COMPILED = True
    PREFAB_FIELDS = ['default', 'default_factory', 'converter', 'init', 'repr', 'kw_only']
    __slots__ = ('default', 'default_factory', 'converter', 'init', 'repr', 'kw_only')
    __match_args__ = ('default', 'default_factory', 'converter', 'init', 'repr', 'kw_only')

    def __init__(self, default=NOTHING, default_factory=NOTHING, converter=None, init: bool=True, repr: bool=True, kw_only: bool=False):
        self.default = default
        self.default_factory = default_factory
        self.converter = converter
        self.init = init
        self.repr = repr
        self.kw_only = kw_only
        self.__prefab_post_init__()

    def __repr__(self):
        return f'{type(self).__qualname__}(default={self.default!r}, default_factory={self.default_factory!r}, converter={self.converter!r}, init={self.init!r}, repr={self.repr!r}, kw_only={self.kw_only!r})'

    def __eq__(self, other):
        return (self.default, self.default_factory, self.converter, self.init, self.repr, self.kw_only) == (other.default, other.default_factory, other.converter, other.init, other.repr, other.kw_only) if self.__class__ == other.__class__ else NotImplemented

    def __prefab_post_init__(self):
        if not self.init and self.default is NOTHING and (self.default_factory is NOTHING):
            raise LivePrefabError('Must provide a default value/factory if the attribute is not in init.')
        if self.kw_only and (not self.init):
            raise LivePrefabError('Attribute cannot be keyword only if it is not in init.')
        if self.default is not NOTHING and self.default_factory is not NOTHING:
            raise LivePrefabError('Cannot define both a default value and a default factory.')