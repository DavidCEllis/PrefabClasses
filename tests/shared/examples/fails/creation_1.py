from prefab_classes import prefab, attribute


@prefab
class Construct:
    x = attribute(default="test", kw_only=True, init=False)
