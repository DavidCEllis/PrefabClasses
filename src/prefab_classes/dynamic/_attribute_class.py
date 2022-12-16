# DO NOT MANUALLY EDIT THIS FILE
# THIS MODULE IS AUTOMATICALLY GENERATED FROM _attribute_template.py
# BY regenerate_attribute.py
# MODIFY THOSE MODULES AND RERUN regenerate_attribute.py

from ..sentinels import NOTHING
from ..exceptions import LivePrefabError

class Attribute:
    COMPILED = True
    PREFAB_FIELDS = ['default', 'default_factory', 'converter', 'init', 'repr', 'kw_only', 'exclude_field', '_type']
    __slots__ = ('default', 'default_factory', 'converter', 'init', 'repr', 'kw_only', 'exclude_field', '_type')
    __match_args__ = ('default', 'default_factory', 'converter', 'init', 'repr', 'kw_only', 'exclude_field', '_type')

    def __init__(self, default=NOTHING, default_factory=NOTHING, converter=None, init: bool=True, repr: bool=True, kw_only: bool=False, exclude_field: bool=False):
        self.__prefab_pre_init__(init=init, default=default, default_factory=default_factory, kw_only=kw_only)
        self.default = default
        self.default_factory = default_factory
        self.converter = converter
        self.init = init
        self.repr = repr
        self.kw_only = kw_only
        self.exclude_field = exclude_field
        self._type = NOTHING

    def __repr__(self):
        return f'{type(self).__qualname__}(default={self.default!r}, default_factory={self.default_factory!r}, converter={self.converter!r}, init={self.init!r}, repr={self.repr!r}, kw_only={self.kw_only!r}, exclude_field={self.exclude_field!r})'

    @staticmethod
    def __prefab_pre_init__(init, default, default_factory, kw_only):
        if not init and default is NOTHING and (default_factory is NOTHING):
            raise LivePrefabError('Must provide a default value/factory if the attribute is not in init.')
        if kw_only and (not init):
            raise LivePrefabError('Attribute cannot be keyword only if it is not in init.')
        if default is not NOTHING and default_factory is not NOTHING:
            raise LivePrefabError('Cannot define both a default value and a default factory.')