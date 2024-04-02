from prefab_classes import prefab, attribute


@prefab
class B:
    x: int
    y: int


@prefab
class C(B):
    x: int = 2
