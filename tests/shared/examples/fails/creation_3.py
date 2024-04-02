from prefab_classes import prefab, attribute


@prefab
class FailFactorySyntax:
    x = attribute(default_factory=list)
    y = attribute()
