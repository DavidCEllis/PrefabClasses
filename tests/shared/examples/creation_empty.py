from typing import ClassVar
from prefab_classes import prefab


@prefab
class Empty:
    pass


@prefab
class EmptyClassVars:
    x: ClassVar = 12


@prefab(iter=True)
class EmptyIter:
    pass
