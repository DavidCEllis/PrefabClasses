# PrefabClasses - Python Class Boilerplate Generator  #
![PrefabClasses Test Status](https://github.com/DavidCEllis/PrefabClasses/actions/workflows/auto_test.yml/badge.svg?branch=main)

Writes the class boilerplate code so you don't have to. 
Yet another variation on attrs/dataclasses.

Unlike `dataclasses` or `attrs`, `prefab_classes` has a
focus on performance and startup time in particular.
This includes trying to minimise the impact of importing
the module itself.

Classes are written lazily when you first access the methods or
eagerly when the module is compiled into a .pyc or rewritten out
to a new .py source file.

The dynamic method of evaluating lazily is more flexible, while
the compiled method is faster (once the .pyc file has been generated).

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

## Why not just use attrs/dataclasses? ##

If attrs or dataclasses solves your problem then you should use them.
They are thoroughly tested, well supported packages. This is a new
project and has not had the rigorous real world testing of either
of those.

Dataclasses/attrs/pydantic all impose some overhead on startup time.
Prefab classes aims to minimise startup time and performance impact
of class generation and in doing so sacrifices some features or 
nice internals of these other implementations.

Import time example:

| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `python -c "pass"` | 26.6 ± 1.2 | 25.0 | 30.6 | 1.00 |
| `python -c "import prefab_classes"` | 28.4 ± 0.4 | 27.6 | 29.5 | 1.07 ± 0.05 |
| `python -c "import dataclasses"` | 48.4 ± 1.0 | 46.5 | 51.5 | 1.82 ± 0.09 |
| `python -c "import attrs"` | 67.3 ± 0.7 | 65.9 | 71.1 | 2.53 ± 0.11 |
| `python -c "import pydantic"` | 105.4 ± 3.4 | 100.3 | 115.7 | 3.96 ± 0.22 |

For more detailed tests you can look at the
[performance section of the docs](https://prefabclasses.readthedocs.io/en/latest/extra/performance_tests.html).

## How does it work ##

The `@prefab` decorator either rewrites the class dynamically, putting methods
in place that will be generated as they are first accessed **OR** it acts
as a marker to indicate the class should be transformed for the compiled
classes.

Compiled classes can both be imported directly or converted back to new .py
files. Direct import will perform the conversion before creating the .pyc file.

example.py
```python
# COMPILE_PREFABS
from prefab_classes import prefab, attribute
from pathlib import Path


@prefab(compile_prefab=True)
class SettingsPath:
    hostname = attribute(default="localhost")
    template_folder = attribute(default='base/path')
    template_name = attribute(default='index')
    file_types = attribute(default_factory=list)

    def __prefab_post_init__(self, template_folder, file_types):
        self.template_folder = Path(template_folder)
        file_types.extend(['.md', '.html'])
        self.file_types = file_types

```

Direct import using prefab_compiler

```python
from prefab_classes_hook import prefab_compiler

with prefab_compiler():
    from example import SettingsPath

# Use normally from here
```

Compile to a new .py file using rewrite_to_py:

```python
>>> from prefab_classes.compiled import rewrite_to_py
>>> rewrite_to_py('example.py', 'example_compiled.py', use_black=True)
```

Using black to format for ease of reading.

example_compiled.py
```python
# DO NOT MANUALLY EDIT THIS FILE
# MODULE: example_compiled.py
# GENERATED FROM: example.py
# USING prefab_classes VERSION: v0.9.1

from pathlib import Path


class SettingsPath:
    COMPILED = True
    PREFAB_FIELDS = ["hostname", "template_folder", "template_name", "file_types"]
    __match_args__ = ("hostname", "template_folder", "template_name", "file_types")

    def __init__(
        self,
        hostname="localhost",
        template_folder="base/path",
        template_name="index",
        file_types=None,
    ):
        self.hostname = hostname
        self.template_name = template_name
        file_types = file_types if file_types is not None else list()
        self.__prefab_post_init__(
            template_folder=template_folder, file_types=file_types
        )

    def __repr__(self):
        return f"{type(self).__qualname__}(hostname={self.hostname!r}, template_folder={self.template_folder!r}, template_name={self.template_name!r}, file_types={self.file_types!r})"

    def __eq__(self, other):
        return (
            (self.hostname, self.template_folder, self.template_name, self.file_types)
            == (
                other.hostname,
                other.template_folder,
                other.template_name,
                other.file_types,
            )
            if self.__class__ == other.__class__
            else NotImplemented
        )

    def __prefab_post_init__(self, template_folder, file_types):
        self.template_folder = Path(template_folder)
        file_types.extend([".md", ".html"])
        self.file_types = file_types
```

If `compile_plain=True` is provided as an argument to `@prefab` the `COMPILED`
and `PREFAB_FIELD` variables will not be set on the class.

## Credit ##

`autogen` function and some magic method definitions taken from 
[David Beazley's Cluegen](https://github.com/dabeaz/cluegen)

General design based on previous experience using
[dataclasses](https://docs.python.org/3/library/dataclasses.html)
and [attrs](https://www.attrs.org/en/stable/) and trying to match the 
requirements for [PEP 681](https://peps.python.org/pep-0681/).
