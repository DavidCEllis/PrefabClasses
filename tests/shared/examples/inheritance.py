# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class InheritObject(object):
    pass


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate:
    x: float
    y: float


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate3D(Coordinate):
    z = attribute()


@prefab(compile_prefab=True, compile_fallback=True)
class CoordinateTime:
    t = attribute()


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate4D(CoordinateTime, Coordinate3D):
    pass


@prefab(compile_prefab=True, compile_fallback=True)
class BasePreInitPostInit:
    def __prefab_pre_init__(self):
        self.pre_init = True

    def __prefab_post_init__(self):
        self.post_init = True


@prefab(compile_prefab=True, compile_fallback=True)
class ChildPreInitPostInit(BasePreInitPostInit):
    pass

# Multiple inheritance inconsistency test classes
# classvar and field should be equal
@prefab(compile_prefab=True, compile_fallback=True)
class Base:
    field: int = 10
    classvar = 10

@prefab(compile_prefab=True, compile_fallback=True)
class Child1(Base):
    pass

@prefab(compile_prefab=True, compile_fallback=True)
class Child2(Base):
    field: int = 50
    classvar = 50

@prefab(compile_prefab=True, compile_fallback=True)
class GrandChild(Child1, Child2):
    pass
