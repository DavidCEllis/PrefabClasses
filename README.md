# PrefabClasses - Python Class Boilerplate Generator  #
![PrefabClasses Test Status](https://github.com/DavidCEllis/PrefabClasses/actions/workflows/auto_test.yml/badge.svg?branch=main)

Writes the class boilerplate code so you don't have to. 
Yet another variation on attrs/dataclasses.

Either written lazily when you first access the methods or
eagerly when the class is compiled into a .pyc. Can optionally
be made to rewrite .py source code with plain classes.

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

This started as a way of investigating how modules like `attrs`
and `dataclasses` work and evolved into an alternative method
of performing a similar task.

### Import Performance ###

There have been 
[some](https://github.com/python-attrs/attrs/issues/575) 
[discussions](https://discuss.python.org/t/improving-dataclasses-startup-performance/15442)
and
[comments](https://github.com/dabeaz/cluegen#wait-hasnt-this-already-been-invented)
about the performance on import of such code generators. 

The first version of the project started with only the `dynamic` form
of construction, based on [David Beazley's Cluegen](https://github.com/dabeaz/cluegen).
Some modifications were needed as I wanted to support more features
such as non-builtin defaults, factories and other options. While this
was an improvement it largely moved the slower parts to happen
at runtime. It would be nice if the 'work' could be done once and then
this result reused so there would be no performance hit.

To this end the 'compiled' method was devised. This works by looking
at the AST of the source, before actual compilation and rewriting
any `@prefab` decorated classes into a regular python class with
all of the standard methods. This is currently **much** slower
than the dynamic method to generate but unlike dynamic classes
this has the benefit of caching and can also output .py source
with the generated classes.

[PEP 638](https://peps.python.org/pep-0638/) appears to be a potential
canonical way of doing such things but it is not actually necessary
to do this as-is. This project provides a method to insert an importer
that will look for a special `# COMPILE_PREFABS` comment and if that
is detected it will handle the AST rewriting before .pyc compilation.

### Why not make this operate on @dataclass? ###

Operating on dataclasses would require matching the dataclasses API and
there are some design choices that dataclasses takes that are either
more difficult to implement in the AST or less flexible than I'd like.

The first obvious difference is dataclasses requires the use of the
type annotation syntax while prefab-classes does not.

For another example dataclasses uses `InitVar` to indicate a value to 
exclude from `__init__` and the field list and all other methods. Special 
annotation instructions are less useful than arguments when working with 
the AST.

An annotation object can be renamed, for example: 
`from dataclasses import InitVar as IV`.
or
`import dataclasses; IV = dataclasses.InitVar`

In the AST all that is easily available is the name `IV` and there is no
way to know if that is `InitVar` without thoroughly inspecting the module
for all of the different ways it could be renamed. 
[Because annotations can be strings this is already awkward even for dataclasses itself](https://github.com/python/cpython/blob/5ee7eb9debb12914f36c5ccee92460a681516fd6/Lib/dataclasses.py#L683-L721).
An argument to `attribute` on the other hand **must** always use the same
name and is much easier to handle. `exclude_field` is a boolean field
that provides similar behaviour for this case.

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
from prefab_classes.compiled import prefab_compiler

with prefab_compiler():
    from example import SettingsPath

# Use normally from here
```

Compile to a new .py file using rewrite_to_py:

```python
>>> from prefab_classes.compiled import rewrite_to_py
>>> rewrite_to_py('example.py', 'example_compiled.py', use_black=True, delete_firstlines=1)
```

Using black to format for ease of reading and deleting the now unused prefab imports.

example_compiled.py
```python
# DO NOT MANUALLY EDIT THIS FILE
# MODULE: example_compiled.py
# GENERATED FROM: example.py
# USING prefab_classes VERSION: v0.7.2

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
