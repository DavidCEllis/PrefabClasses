# Dynamic Construction #

An alternate method for constructing dynamic prefabs is also available
similar to dataclasses' `make_dataclass` or attrs' `make_class`.

```python
from prefab_classes import attribute, build_prefab

BuiltPrefab = build_prefab(
    "BuiltPrefab",
    [
        ("x", attribute(default=0)),
        ("y", attribute(default=1)),
    ],
)
```

Is equivalent to:

```python
from prefab_classes import attribute, prefab

@prefab
class BuiltPrefab:
    x = attribute(default=0)
    y = attribute(default=1)
```

`build_prefab` supports all of the same optional arguments as `prefab` apart from those
related to compilation.

See {doc}`api` for more details
