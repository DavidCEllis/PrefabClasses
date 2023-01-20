# COMPILE_PREFABS
from prefab_classes import prefab, attribute
from decimal import Decimal


@prefab(compile_prefab=True, init=True, repr=True, eq=True, iter=False)
class X:
    v: int
    w: Decimal = attribute(default="3.14", init=True, repr=True, kw_only=False)
    x: list = attribute(default_factory=list, init=True, repr=True, kw_only=True)
    y: str = attribute(kw_only=True)
    z: tuple[int, str] = (42, "trees")

    def __prefab_post_init__(self, w):
        self.w = Decimal(w)
