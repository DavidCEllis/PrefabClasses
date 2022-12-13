# PrefabClasses - Python Class Boilerplate Generator  #
![PrefabClasses Test Status](https://github.com/DavidCEllis/PrefabClasses/actions/workflows/auto_test.yml/badge.svg?branch=main)

Writes the class boilerplate code so you don't have to. 
Yet another variation on attrs/dataclasses.

Either written lazily when you first access the methods or
eagerly when the class is compiled into a .pyc. Can optionally
be made to rewrite .py source code with plain classes.

## Why are you remaking this again? ##

Initially I was just trying to remove a dependency on `attrs`
from a project and used 
[David Beazley's Cluegen](https://github.com/dabeaz/cluegen)
as a starting point. 

Working and modifying that to fit my needs made me think about
coming at the performance problem from the opposite angle. 
Instead of rewriting methods at the last possible point when the 
data is first accessed, rewriting them when they are compiled 
to a .pyc file by modifying the AST.

The benefit of this method is that once the source has been compiled
to a .pyc file there is no longer any overhead from generating the
class methods. The result is a normal python class as if it had been
written by hand. Working solely on the AST does lead to some design
differences from other popular modules like attrs or dataclasses.

There is no benefit from using the compiled version over dynamic
implementations unless the .pyc files are generated and used.

### Dynamic ###

The dynamic method works roughly as *cluegen* worked, generating the 
required methods only when they are first accessed. Compared to
attrs this trades speed of first access for speed of import. 
This also means that if a class method is never accessed then 
it is not generated.

Unlike cluegen this reverts to using a decorator for each class
rather than using inheritance. This is largely due to it being
much easier to identify a specific decorator in the AST to identify
classes to be modified for the compiled version.

### Compiled ###

The 'compiled' method instead generates all of the code when the 
module is first *compiled* into a .pyc file by modifying the AST. 

There are some trade-offs and differences between the two.

* The compiled method uses the **literal names** `prefab` and `attribute`
  to identify classes to be imported and to identify features. 
  If these are changed things will not work.
  * The functions to not technically need to be imported however, unless
    the code should fallback to the dynamic method.
* After the .pyc files have been compiled, compiled classes import
  much more quickly than dynamic ones as they are plain python classes.
    * They are not *quite* as fast as modules with native classes,
      as hash-based invalidation is used instead of timestamp
      invalidation.
* Due to .pyc files being created independently inheritance is
  more restricted for compiled classes.
    * Inheritance across modules is not supported
    * Inheritance from non-prefab base classes is not supported
* As the classes must be compiled into the .pyc files, compiled
  classes can't be created interactively.
* In order to compile classes a `# COMPILE_PREFABS` comment must
  be at the top of a module. The module must also be imported in
  a `with prefab_compiler():` block.
    * This places an import hook that will compile prefabs in
      these files.
* Compiled classes support slots, dynamic classes do not.
    * While `attrs` supports this dynamically, it is forced to 
      make a new class and copy over features. This can have some
      side effects.

## Usage Examples ##

Usage for the dynamic form is pretty much what you would expect:

```python
from prefab_classes import attribute, prefab
   

@prefab
class Coordinate:
    x: float
    y: float


@prefab
class Coordinate3D(Coordinate):
    z: float = 0.0

>>> point = Coordinate3D(1, 2)
Coordinate3D(x=1, y=2, z=0)
>>> point.x, point.y, point.z
(1, 2, 0)

from pathlib import PurePath

@prefab
class Settings:
    hostname = attribute(default="localhost")
    template_folder = attribute(default='base/path', converter=PurePath)


>>> settings = Settings(hostname='127.0.0.1')
>>> settings.template_folder
PureWindowsPath('base/path')
```

Usage for the 'compiled' form is slightly more complicated.

example_compiled.py
```python
# COMPILE_PREFABS
from prefab_classes import prefab

@prefab(compile_prefab=True)
class Settings:
    hostname: str = "localhost"
    template_folder: str = 'base/path'
```

The prefab will then be compiled to a .pyc file when imported in another file
with the import hook included. The resulting code can be previewed using the 
`preview` function. If `black` is installed, the code will be run through 
to make the result more readable, to avoid this use `use_black=false`.

`from prefab_classes.compiled import preview`
`preview('example_compiled.py')`
```python
from prefab_classes import prefab

class Settings:
    COMPILED = True
    PREFAB_FIELDS = ["hostname", "template_folder"]

    def __init__(self, hostname: str = "localhost", template_folder: str = "base/path"):
        self.hostname = hostname
        self.template_folder = template_folder

    def __repr__(self):
        return f"Settings(hostname={self.hostname!r}, template_folder={self.template_folder!r})"

    def __eq__(self, other):
        return (
            (self.hostname, self.template_folder)
            == (other.hostname, other.template_folder)
            if self.__class__ == other.__class__
            else NotImplemented
        )
```

In order to convert the class on the generation of the .pyc the imports must be done
with the prefab compiler import hook in place. This is done using the prefab_compiler
context manager before imports.

use_compiled.py
```python
from prefab_classes import prefab_compiler

with prefab_compiler():
    from example_compiled import Settings
...
```
