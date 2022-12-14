# Getting Started #

Prefab Classes is designed to work much like dataclasses, using different
underlying methods. The basics should be familiar but there are some 
differences documented here: {doc}`extra/dataclasses_differences`.

The prefab_classes package provides two main functions in order to assist in
instructing the module on how you want your classes to be written.

The `@prefab` decorator instructs the module that the decorated class should
be rewritten with some options for which methods to generate. The `attribute`
function provides instructions for how to handle a specific field.

## Basic Usage ##

greeting.py
```python
from prefab_classes import prefab

@prefab
class Greeting:
    greeting: str = "Hello"
    
    def greet(self):
        print(f"{self.greeting} World!")
```

```python
>>> from greeting import Greeting
>>> hello = Greeting()
>>> hello.greet()
Hello World!

>>> hello
Greeting(greeting='Hello')

>>> hello.greeting
'Hello'

>>> goodbye = Greeting("Goodbye")
>>> hello == goodbye
False

>>> goodbye
Greeting(greeting='Goodbye')
```

## Compilation ##

The `@prefab` decorator can also be used to intruct the module to compile
the decorated class and generate the methods before the .py file is converted
to a .pyc.

This is done by parsing the AST of the module and creating the methods there
instead of creating them dynamically when the code is running. This does pose
some additional restrictions - for more detail see
{doc}`dynamic_and_compiled`.

In order for this to work correctly a special `# COMPILE_PREFABS` comment is
needed at the top of the file. This directs the importer to process the 
following file while any other files are passed on to Python's standard
importer.

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
from prefab_classes import prefab_compiler

with prefab_compiler():
    from example import SettingsPath

# Use normally from here
```

Alternatively the module can be converted back from the AST to a python file.

By default these are exactly as they return from the `ast.unparse` function,
comments are stripped by the AST parsing stage and all fomatting is lost.
If `black` is installed there is the option to pass the code through the
formatter to make it a little more readable. 

The `delete_firstlines` argument is provided so a prefab_classes import 
can be removed if placed at the top of the file, saving the import time 
if the module is not needed in the compiled form.

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