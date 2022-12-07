from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class KWBasic:
    x = attribute(kw_only=True)
    y = attribute(kw_only=True)
