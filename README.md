# PrefabClasses - Python Class Boilerplate Generator  #
![PrefabClasses Test Status](https://github.com/DavidCEllis/PrefabClasses/actions/workflows/auto_test.yml/badge.svg?branch=main)

Writes the class boilerplate code so you don't have to. 
Yet another variation on attrs/dataclasses.

Unlike `dataclasses` or `attrs`, `prefab_classes` has a
focus on performance and startup time in particular.
This includes trying to minimise the impact of importing
the module itself.

Classes are written lazily when their methods are first needed.

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

## Slots ##

There is new support for creating classes defined via `__slots__` using a SlotAttributes instance.

Similarly to the type hinted form, plain values given to a SlotAttributes instance are treated as defaults
while `attribute` calls are handled normally. `doc` values will be seen when calling `help(...)` on the class
while the `__annotations__` dictionary will be updated with `type` values given. Annotations can also still
be given normally (which will probably be necessary for static typing tools).

```python
from prefab_classes import prefab, attribute, SlotAttributes

@prefab
class Settings:
    __slots__ = SlotAttributes(
        hostname="localhost",
        template_folder="base/path",
        template_name=attribute(default="index", type=str, doc="Name of the template"),
    )
```

### Why not make slots an argument to the decorator like dataclasses (or attrs)? ###

Because this doesn't work properly.

When you make a slotted dataclass the decorator actually has to create a new class and copy everything defined
on the original class over because it is impossible to set *functional* slots on a class that already exists.
This leads to some subtle bugs if anything ends up referring to the original class
(ex: method decorators that rely on the class or [the `super()` function in a method](https://github.com/python/cpython/pull/111538)).

```python
from dataclasses import dataclass
from prefab_classes import prefab, SlotAttributes

cache = {}
def cacher(cls):
    cache[cls.__name__] = cls
    return cls

@dataclass(slots=True)
@cacher
class DataclassSlots:
    pass

@prefab
@cacher
class PrefabSlots:
    __slots__ = SlotAttributes()
    
print(f"{cache['DataclassSlots'] is DataclassSlots = }")  # False
print(f"{cache['PrefabSlots'] is PrefabSlots = }")  # True
```

By contrast, by using `__slots__` ability to use a mapping as input `@prefab` does not need to create a new
class and can simply modify the original in-place. Once done `__slots__` is replaced with a dict containing
the same keys and any docs provided that can be rendered via `help(...)`.

## Why not just use attrs or dataclasses? ##

If attrs or dataclasses solves your problem then you should use them.
They are thoroughly tested, well supported packages. This is a new
project and has not had the rigorous real world testing of either
of those.

Prefab Classes has been created for situations where startup time is important, 
such as for CLI tools and for handling conversion of inputs in a way that
was more useful to me than attrs converters (`__prefab_post_init__`).

For example looking at import time (before any classes have been generated).

| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `python -c "pass"` | 22.7 ± 0.8 | 21.4 | 24.9 | 1.00 |
| `python -c "from prefab_classes import prefab"` | 23.9 ± 1.0 | 23.0 | 27.1 | 1.06 ± 0.06 |
| `python -c "from collections import namedtuple"` | 23.6 ± 0.5 | 22.9 | 24.9 | 1.04 ± 0.04 |
| `python -c "from typing import NamedTuple"` | 31.3 ± 0.4 | 30.7 | 32.7 | 1.38 ± 0.05 |
| `python -c "from dataclasses import dataclass"` | 38.0 ± 0.5 | 36.9 | 38.9 | 1.68 ± 0.06 |
| `python -c "from attrs import define"` | 52.1 ± 0.8 | 50.7 | 54.0 | 2.30 ± 0.09 |
| `python -c "from pydantic import BaseModel"` | 70.0 ± 3.7 | 65.6 | 79.3 | 3.09 ± 0.20 |



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
`dataclasses` generates all of its methods when the class is created.

## On using an approach vs using a tool ##

As this module's code generation is based on the workings of [David Beazley's Cluegen](https://github.com/dabeaz/cluegen)
I thought it was briefly worth discussing his note on learning an approach vs using a tool.

This project arose as a result of looking at my own approach to the same problem, based on
extending the workings of `cluegen`. I found there were some features I needed for 
the projects I was working on (the first instance being that `cluegen` doesn't support 
defaults that aren't builtins). 

This grew and on making further extensions and customising the project to my needs I found 
I wanted to use it in all of my projects and the easiest way to do this and keep things 
in sync was to publish it as a tool on PyPI.

It has only 1 dependency at runtime which is a small library I've created to handle lazy 
imports. This is used to provide easy access to functions for the user while keeping the
overall import time low. It's also used internally to defer some methods from being imported
(eg: if you never look at a `__repr__`, then you don't need to import `reprlib.recursive_repr`).
Unfortunately this raises the base import time but it's still a lot faster than `import typing`.

So this is the tool I've created for my use using the approach I've come up with to suit my needs.
You are welcome to use it if you wish - and if it suits your needs better than `attrs` or 
`dataclasses` then good. I'm glad you found this useful.

## Credit ##

`autogen` function and some magic method definitions taken from 
[David Beazley's Cluegen](https://github.com/dabeaz/cluegen)

General design based on previous experience using
[dataclasses](https://docs.python.org/3/library/dataclasses.html)
and [attrs](https://www.attrs.org/en/stable/) and trying to match the 
requirements for [PEP 681](https://peps.python.org/pep-0681/).
