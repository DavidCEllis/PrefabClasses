# COMPILE_PREFABS
from prefab_classes import prefab, attribute
from decimal import Decimal


@prefab(compile_prefab=True, init=True, repr=True, eq=True, iter=False)
class Y:
    v: int = 3  # Should be ignored
    w = attribute(default="3.14", init=True, repr=True, kw_only=False)
    x = attribute(default_factory=list, init=True, repr=True, kw_only=True)
    y = attribute(kw_only=True)
    z = attribute(default=(42, "trees"))

    def __prefab_post_init__(self, w):
        self.w = Decimal(w)
