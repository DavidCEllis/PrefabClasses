# COMPILE_PREFABS
from prefab_classes import prefab, attribute, KW_ONLY


@prefab(compile_prefab=True, compile_fallback=True)
class KWBasic:
    x = attribute(kw_only=True)
    y = attribute(kw_only=True)


@prefab(compile_prefab=True, compile_fallback=True)
class KWOrdering:
    x = attribute(default=2, kw_only=True)
    y = attribute()


@prefab(compile_prefab=True, compile_fallback=True)
class KWBase:
    x = attribute(default=2, kw_only=True)


@prefab(compile_prefab=True, compile_fallback=True)
class KWChild(KWBase):
    y = attribute()


@prefab(compile_prefab=True, compile_fallback=True, kw_only=True)
class KWPrefabArgument:
    x = attribute()
    y = attribute()


@prefab(compile_prefab=True, compile_fallback=True, kw_only=True)
class KWPrefabArgumentOverrides:
    x = attribute()
    y = attribute(kw_only=False)


@prefab(compile_prefab=True, compile_fallback=True)
class KWFlagNoDefaults:
    x: int
    _: KW_ONLY
    y: int


@prefab(compile_prefab=True, compile_fallback=True)
class KWFlagXDefault:
    x: int = 1
    _: KW_ONLY
    y: int
