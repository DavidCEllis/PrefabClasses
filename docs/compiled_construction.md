# Compiling Prefabs #

The `@prefab` decorator can also be used to intruct the module to compile
the decorated class and generate the methods before the .py file is converted
to a .pyc.

## Using the importer ##

In order to compile the classes 3 extra steps are needed:

1. Provide `compile_prefab=True` to the `prefab` decorator
2. Place a `# COMPILE_PREFABS` comment at the top of the .py file
3. Insert the import hook from `prefab_classes.hook` before importing the module

The compilation is done by parsing the AST of the module and creating the methods 
there before the file is processed and converted to a .pyc. This means that after
the first run where this compilation take place, provided the import hook is still
used the .pyc will be imported with the classes already compiled.

Here's an example of the usage:

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

Compiled prefabs can be used directly on import by using the prefab_compiler.

```python
from prefab_classes.hook import prefab_compiler

with prefab_compiler():
    from example import SettingsPath

# Use normally from here
```

## Generate source code output ##

Alternatively the module can be converted back from the AST to a python file.

This is provided as there are some cases where a pre-processed source code file
may be usable where an import hook is not. This is actually used inside 
`prefab_classes` to generate the code for the `Attribute` class for dynamic
prefabs.

By default the output is exactly as returned from the `ast.unparse` function,
comments are stripped by the AST parsing stage and all fomatting is lost.
If `black` is installed there is the option to pass the code through the
formatter to make it a little more readable.

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

## Additional Tools ##

The `prefab_classes.compiled` module provides some additional tools for working with compiled classes.

`preview` can be used to quickly show what a .py file will compile to. This is intended to be used as 
a quick checking tool when creating compiled prefabs or when learning how to use the module. It 
automatically defaults to using `black` formatting if the module is installed to make the output
more readable in the terminal.

`get_sources_to_compare` is a tool intended to assist in testing. If prefab_classes is being used
to generate source files via `rewrite_to_py` then `get_sources_to_compare` takes the same arguments
and gives you the code for both the original file converted and what you currently have as your
output file. This is useful as a check to make sure you haven't changed the 'template' code without
regenerating the output.
