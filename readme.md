# PrefabClasses - Clueless cluegen #

Class boilerplate generator. Yet another variation on attrs/dataclasses.

# Why are you remaking this again? #

Initially wanting to remove a dependency on attrs I had seen 
[David Beazley's Cluegen](https://github.com/dabeaz/cluegen)
and wanted to see if something like that could work for the 
project. With some modification I ended up with the first
version of this. 

**The 'compiled' method has not yet been implemented in this
package but soon will be. 
See [PrefabGenerator](https://github.com/DavidCEllis/PrefabGenerator)
for the proof of concept.**

This package provides 2 different methods of code generation
depending on the use case and speed requirements.

The 'live' method works as *cluegen* worked, generating the 
required methods only when they are first accessed. Compared to
attrs this trades speed of first access for speed of import. 
This also means that if a class method is never accessed then 
it is not generated.

The 'compiled' method instead generates all of the code when the 
module is first *compiled* into a .pyc file. Subsequently there 
is no overhead once the .pyc has been generated as the result 
is a plain python class in the .pyc. The trade-off is that this
method has some additional restrictions so is slightly less
flexible. Most notably inheritance does not work across .py files
as each file is compiled in isolation.

Usage is pretty much what you would expect:

```python
from prefab_classes import Attribute, prefab
   

@prefab
class Coordinate:
    x = Attribute()
    y = Attribute()


@prefab
class Coordinate3D(Coordinate):
    z = Attribute(default=0)

>>> point = Coordinate3D(1, 2)
Coordinate3D(x=1, y=2, z=0)
>>> point.x, point.y, point.z
(1, 2, 0)

from pathlib import PurePath

@prefab
class Settings:
    hostname = Attribute(default="localhost")
    template_folder = Attribute(default='base/path', converter=PurePath)


>>> settings = Settings(hostname='127.0.0.1')
>>> settings.template_folder
PureWindowsPath('base/path')
```
