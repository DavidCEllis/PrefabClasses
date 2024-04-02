from prefab_classes import prefab, attribute


@prefab
class B:
    x: int = 0


@prefab
class C(B):
    y: int
