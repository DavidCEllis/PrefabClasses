from prefab_classes import prefab, attribute


@prefab
class FailSyntax:
    x = attribute(default=0)
    y = attribute()
