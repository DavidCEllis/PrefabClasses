# Prefab - Clueless cluegen #

Class boilerplate generator.

Much of the code is based on [David Beazley's Cluegen](https://github.com/dabeaz/cluegen)
rewritten with additional comments to remind me of how it works.

This was done both as a means of learning how descriptors work and to remove a dependency 
on attrs from a project.

Much like cluegen, I'm not making a package of this.

This doesn't use type hints (clues) and instead uses a separate descriptor class
to define Attributes. The attributes 'register' themselves with the class through
the (ab)use of the `__set_name__` magic method.

Usage is pretty much what you would expect:

```python
from prefab import Attribute, Prefab
   

class Coordinate(Prefab):
    x = Attribute()
    y = Attribute()


class Coordinate3D(Coordinate):
    z = Attribute(default=0)

>>> point = Coordinate3D(1, 2)
Coordinate3D(x=1, y=2, z=0)
>>> point.x, point.y, point.z
(1, 2, 0)

from pathlib import PurePosixPath

class Settings(Prefab):
    hostname = Attribute(default="localhost")
    template_folder = Attribute(default='base/path', converter=PurePosixPath)


>>> settings = Settings(hostname='127.0.0.1')
>>> settings.template_folder
PurePosixPath('base/path')
```
