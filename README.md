# PrefabClasses - Python Class Boilerplate Generator  #
![PrefabClasses Test Status](https://github.com/DavidCEllis/PrefabClasses/actions/workflows/auto_test.yml/badge.svg?branch=main)

Writes the class boilerplate code so you don't have to. 
Yet another variation on attrs/dataclasses.

Unlike `dataclasses` or `attrs`, `prefab_classes` has a
focus on performance and startup time in particular.
This includes trying to minimise the impact of importing
the module itself.

Classes are written lazily when their methods are first needed.

> [!WARNING]
> There is a second form of generation that works by modifying the AST, however
> this is deprecated and will be removed in the next major version.
> It required placing an import hook in order to use it and it was complex to maintain.

For more detail look at the [documentation](https://prefabclasses.readthedocs.io).

## Usage ##

Define the class using plain assignment and `attribute` function calls:

```python
from prefab_classes import prefab, attribute

@prefab
class Settings:
    hostname = attribute(default="localhost")
    template_folder = attribute(default='base/path')
    template_name = attribute(default='index')
```

Or with type hinting:

```python
from prefab_classes import prefab

@prefab
class Settings:
    hostname: str = "localhost"
    template_folder: str = 'base/path'
    template_name: str = 'index'
```

In either case the result behaves the same.

```python
>>> from prefab_classes.funcs import to_json
>>> s = Settings()
>>> print(s)
Settings(hostname='localhost', template_folder='base/path', template_name='index')
>>> to_json(s)
'{"hostname": "localhost", "template_folder": "base/path", "template_name": "index"}'
```

For further details see the `usage` pages in the documentation.

There is experimental support for creating classes defined via `__slots__` using a PrefabSlots instance.

Similarly to the type hinted form, plain values given to a PrefabSlots instance are treated as defaults
while `attribute` calls are handled normally. `doc` values will be seen when calling `help(...)` on the class
while the `__annotations__` dictionary will be updated with `type` values given. Annotations can also still
be given normally (which will probably be necessary for static typing tools).

```python
from prefab_classes import prefab, attribute, PrefabSlots

@prefab
class Settings:
    __slots__ = PrefabSlots(
        hostname="localhost",
        template_folder="base/path",
        template_name=attribute(default="index", type=str, doc="Name of the template"),
    )
    
```

## Why not just use attrs/dataclasses? ##

If attrs or dataclasses solves your problem then you should use them.
They are thoroughly tested, well supported packages. This is a new
project and has not had the rigorous real world testing of either
of those.

Prefab Classes has been created for situations where startup time is important, 
such as for CLI tools. 

For example looking at import time (before any classes have been generated).

| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `python -c "pass"` | 21.5 ± 0.3 | 20.9 | 23.0 | 1.00 |
| `python -c "from collections import namedtuple"` | 23.7 ± 0.5 | 22.8 | 25.4 | 1.10 ± 0.03 |
| `python -c "from prefab_classes import prefab"` | 24.2 ± 0.4 | 23.5 | 25.9 | 1.13 ± 0.03 |
| `python -c "from typing import NamedTuple"` | 31.1 ± 0.4 | 30.4 | 32.6 | 1.45 ± 0.03 |
| `python -c "from dataclasses import dataclass"` | 38.1 ± 0.6 | 37.1 | 40.6 | 1.77 ± 0.04 |
| `python -c "from attrs import define"` | 51.8 ± 1.3 | 50.5 | 57.7 | 2.41 ± 0.07 |
| `python -c "from pydantic import BaseModel"` | 67.4 ± 1.1 | 65.9 | 71.7 | 3.13 ± 0.07 |


For more detailed tests you can look at the
[performance section of the docs](https://prefabclasses.readthedocs.io/en/latest/extra/performance_tests.html).

## How does it work ##

The `@prefab` decorator analyses the class it is decorating and prepares an internals dict, along
with performing some other early checks (this may potentially be deferred in a future update,
**do not depend on any of the prefab internals directly**). Once this is done it sets any direct
values (`PREFAB_FIELDS` and `__match_args__` if required) and places non-data descriptors for
all of the magic methods to be generated.

The non-data descriptors for each of the magic methods perform code generation when first called
in order to generate the actual methods. Once the method has been generated, the descriptor is 
replaced on the class with the resulting method so there is no overhead regenerating the method
on each access. 

By only generating methods the first time they are used the start time can be
improved and methods that are never used don't have to be created at all (for example the 
`__repr__` method is useful when debugging but may not be used in normal runtime). In contrast
`dataclasses` generates all of its methods when the class is created..

## Credit ##

`autogen` function and some magic method definitions taken from 
[David Beazley's Cluegen](https://github.com/dabeaz/cluegen)

General design based on previous experience using
[dataclasses](https://docs.python.org/3/library/dataclasses.html)
and [attrs](https://www.attrs.org/en/stable/) and trying to match the 
requirements for [PEP 681](https://peps.python.org/pep-0681/).
