# Importing from the 'wrong' place #

If you've looked at the source code for prefab_classes you may have noticed
that some standard library functions and classes are not being imported from
their publicly available locations.

While making this I've discovered that some of these 'correct' places to 
import modules come with significant performance penalties for startup time. 
The exact same objects are often actually defined in completely different 
places with far quicker import times, sometimes already being imported by 
python's startup.

Generally this isn't recommended but it's something I've ended up doing while
trying to absolutely minimise the startup impact of both dynamic and compiled
prefabs. If the modules did not impose this performance penalty this would be 
unnecessary.

The timings are not completely stable on my machine but give a sense of the
scale.

## site ##

The `site` package is always imported by python on load provided it is not 
specifically excluded. It's necessary to import modules as you would normally
expect. As this is always here it has been removed from the importtimes in 
when discussing the other modules.

Arrows have been added to indicate modules mentioned later.

`python -X importtime -c "pass"`

```
import time: self [us] | cumulative | imported package
import time:       467 |        467 |   _io
import time:        50 |         50 |   marshal
import time:       328 |        328 |   posix
import time:       401 |       1244 | _frozen_importlib_external <-- importlib
import time:       907 |        907 |   time
import time:       157 |       1063 | zipimport
import time:       128 |        128 |     _codecs
import time:       612 |        739 |   codecs
import time:       714 |        714 |   encodings.aliases
import time:      1296 |       2748 | encodings
import time:       261 |        261 | encodings.utf_8
import time:        96 |         96 | _signal
import time:        53 |         53 |     _abc
import time:       176 |        229 |   abc
import time:       230 |        459 | io
import time:        48 |         48 |       _stat
import time:        60 |        107 |     stat
import time:       775 |        775 |     _collections_abc <-- collections.abc
import time:        35 |         35 |       genericpath
import time:        63 |         98 |     posixpath
import time:       303 |       1281 |   os
import time:        65 |         65 |   _sitebuiltins
import time:       616 |        616 |   _distutils_hack
import time:       154 |        154 |   sitecustomize
import time:      1535 |       3650 | site
```

Note that having some packages installed can change this and make the start time
slower. For instance having `sphinx` installed results in this result for the
same command:

```
import time: self [us] | cumulative | imported package
import time:       168 |        168 |   _io
import time:        35 |         35 |   marshal
import time:       279 |        279 |   posix
import time:       326 |        807 | _frozen_importlib_external
import time:       557 |        557 |   time
import time:       120 |        676 | zipimport
import time:        46 |         46 |     _codecs
import time:       296 |        342 |   codecs
import time:       592 |        592 |   encodings.aliases
import time:       724 |       1658 | encodings
import time:       238 |        238 | encodings.utf_8
import time:       102 |        102 | _signal
import time:        30 |         30 |     _abc
import time:       114 |        144 |   abc
import time:       146 |        290 | io
import time:        43 |         43 |       _stat
import time:        52 |         94 |     stat
import time:       707 |        707 |     _collections_abc
import time:        32 |         32 |       genericpath
import time:        55 |         86 |     posixpath
import time:       295 |       1181 |   os
import time:        58 |         58 |   _sitebuiltins
import time:       559 |        559 |   _distutils_hack
import time:       443 |        443 |   types
import time:       335 |        335 |       warnings
import time:       404 |        738 |     importlib
import time:       291 |        291 |     importlib._abc
import time:       104 |        104 |         itertools
import time:       201 |        201 |         keyword
import time:        93 |         93 |           _operator
import time:       365 |        457 |         operator
import time:       242 |        242 |         reprlib
import time:        73 |         73 |         _collections
import time:      1014 |       2089 |       collections
import time:        66 |         66 |         _functools
import time:       723 |        788 |       functools
import time:       764 |       3640 |     contextlib
import time:       154 |       4821 |   importlib.util
import time:        60 |         60 |   importlib.machinery
import time:        85 |         85 |   sitecustomize
import time:      3833 |      11036 | site
```

## prefab_classes and prefab_classes.hook ##

> ** Note **
> 
> This section is outdated as of v0.10.0
>
> v0.10.0 switched to using `ducktools.lazyimporter` and made some imports lazy to 
> allow for faster access to functions at the cost of slightly slower complete import.
> `prefab_classes_hook` has also been moved back to `prefab_classes.hook` as a result.

For a baseline for these comparisons here are import times for prefab_classes v0.9.1

`python -X importtime -c "import prefab_classes"`

```
import time: self [us] | cumulative | imported package
...
import time:       161 |        161 |       prefab_classes._typing
import time:       152 |        152 |         prefab_classes.sentinels
import time:       179 |        179 |         prefab_classes.exceptions
import time:       174 |        504 |       prefab_classes.dynamic._attribute_class
import time:       128 |        128 |       prefab_classes.constants
import time:       124 |        124 |         prefab_classes.dynamic.autogen
import time:       275 |        398 |       prefab_classes.dynamic.method_generators
import time:       455 |       1643 |     prefab_classes.dynamic.prefab
import time:       229 |       1872 |   prefab_classes.dynamic
import time:       333 |       2205 | prefab_classes
```

`prefab_classes_hook` is slightly more complicated as for the first compilation extra
modules are imported, but after this initial compilation if a cached .pyc file is found
no extra modules are loaded.

These example scripts are used to show the difference in compilation and subsequent runs.

`prefab_compiled_data.py`

```python
# COMPILE_PREFABS
from prefab_classes import prefab

@prefab(compile_prefab=True)
class C0:
    a: int
    b: int
    c: int
    d: int
    e: int

C0.__init__, C0.__repr__, C0.__eq__
```

`prefab_compiled_example.py`

```python
from prefab_classes_hook import prefab_compiler

with prefab_compiler():
    import prefab_compiled_data
```

`python -X importtime prefab_compiled_example.py`

First run:

```
import time: self [us] | cumulative | imported package
...
import time:       437 |        437 |   prefab_classes_hook.import_hook
import time:       392 |        828 | prefab_classes_hook
import time:       216 |        216 |             prefab_classes._typing
import time:       231 |        231 |               prefab_classes.sentinels
import time:       259 |        259 |               prefab_classes.exceptions
import time:       246 |        735 |             prefab_classes.dynamic._attribute_class
import time:       193 |        193 |             prefab_classes.constants
import time:       195 |        195 |               prefab_classes.dynamic.autogen
import time:       336 |        531 |             prefab_classes.dynamic.method_generators
import time:       444 |       2118 |           prefab_classes.dynamic.prefab
import time:       372 |       2489 |         prefab_classes.dynamic
import time:       473 |       2962 |       prefab_classes
import time:       285 |        285 |       prefab_classes.compiled.rewrite_source
import time:       219 |       3465 |     prefab_classes.compiled
import time:      1116 |       1116 |       _ast
import time:       104 |        104 |           itertools
import time:       319 |        319 |           keyword
import time:       718 |        718 |             _operator
import time:       502 |       1220 |           operator
import time:       331 |        331 |           reprlib
import time:        58 |         58 |           _collections
import time:      1026 |       3055 |         collections
import time:       463 |        463 |           types
import time:       129 |        129 |           _functools
import time:       690 |       1281 |         functools
import time:       807 |       5141 |       contextlib
import time:      1520 |       1520 |       enum
import time:      1553 |       9328 |     ast
import time:       900 |      13692 |   prefab_classes.compiled.generator
import time:      1312 |       1312 |       warnings
import time:       560 |       1871 |     importlib
import time:       816 |        816 |     importlib._abc
import time:       228 |       2913 |   importlib.util
import time:        74 |         74 |         _sre
import time:       490 |        490 |           re._constants
import time:       484 |        974 |         re._parser
import time:       314 |        314 |         re._casefix
import time:       516 |       1876 |       re._compiler
import time:       401 |        401 |       copyreg
import time:       728 |       3005 |     re
import time:       408 |        408 |     token
import time:      1267 |       4679 |   tokenize
import time:      2583 |      23866 | prefab_compiled_data
```

Subsequent runs:

```
import time: self [us] | cumulative | imported package
...
import time:       456 |        456 |   prefab_classes_hook.import_hook
import time:       298 |        753 | prefab_classes_hook
import time:       287 |        287 | prefab_compiled_data
```

## collections.abc ##

The `collections.abc` module used for some typing objects is actually defined
in a file called `_collections_abc.py` and is imported by python on load.

Importing from `collections.abc` also forces the import of the `collections`
module itself.

`python -X importtime -c "import collections.abc"`

```
import time: self [us] | cumulative | imported package
...
import time:       126 |        126 |     itertools
import time:       252 |        252 |     keyword
import time:        82 |         82 |       _operator
import time:       437 |        519 |     operator
import time:       281 |        281 |     reprlib
import time:        66 |         66 |     _collections
import time:      1218 |       2459 |   collections
import time:       255 |       2714 | collections.abc
```

Note - this is the source code for `abc.py` in `collections`:

```python
from _collections_abc import *
from _collections_abc import __all__
from _collections_abc import _CallableGenericAlias
```

As shown earlier `_collections_abc` is already imported by `site`

## importlib.util and importlib.machinery ##

In some places in the code you'll see that I've ignored the lovely

**This module is NOT meant to be directly imported!**

warning at the top of `_bootstrap_external.py` and directly imported
its frozen version `_frozen_importlib_external`. This is done both
because `importlib.util` is far too slow of an import and as it's 
already in use I might as well take the smaller performance benefit 
from sidestepping `importlib.machinery` too.

`python -X importtime -c "import importlib.util"`

```
import time: self [us] | cumulative | imported package
...
import time:       483 |        483 |     warnings
import time:       341 |        823 |   importlib
import time:       282 |        282 |   importlib._abc
import time:       208 |        208 |       itertools
import time:       233 |        233 |       keyword
import time:        79 |         79 |         _operator
import time:       360 |        438 |       operator
import time:       260 |        260 |       reprlib
import time:        80 |         80 |       _collections
import time:      1025 |       2242 |     collections
import time:       335 |        335 |       types
import time:        59 |         59 |       _functools
import time:       700 |       1092 |     functools
import time:       822 |       4155 |   contextlib
import time:       152 |       5410 | importlib.util
```

`python -X importtime -c "import importlib.machinery"`

```
import time: self [us] | cumulative | imported package
...
import time:       541 |        541 |     warnings
import time:       536 |       1076 |   importlib
import time:        68 |       1144 | importlib.machinery
```

`_frozen_importlib_external` is imported already and so has no import
penalty.

By not importing from `importlib.machinery` the import hook loads ~2x faster
and by not importing from `importlib.util` it's ~7x faster.

`importlib.util` is still used directly when first compiling prefabs as
performance is less critical at that point.


## typing ##

I don't think it needs to be said that `import typing` is slow, but in case
you weren't already aware.

`python -X importtime -c "import typing"`

```
import time: self [us] | cumulative | imported package
...
import time:       119 |        119 |     itertools
import time:       266 |        266 |     keyword
import time:       140 |        140 |       _operator
import time:       450 |        589 |     operator
import time:       275 |        275 |     reprlib
import time:        67 |         67 |     _collections
import time:      1052 |       2366 |   collections
import time:       257 |        257 |   collections.abc
import time:       384 |        384 |       types
import time:        82 |         82 |       _functools
import time:       857 |       1322 |     functools
import time:       690 |       2011 |   contextlib
import time:      2308 |       2308 |     enum
import time:        75 |         75 |       _sre
import time:       402 |        402 |         re._constants
import time:       386 |        788 |       re._parser
import time:       166 |        166 |       re._casefix
import time:       468 |       1494 |     re._compiler
import time:       268 |        268 |     copyreg
import time:       587 |       4656 |   re
import time:       340 |        340 |   warnings
import time:       338 |        338 |   _typing
import time:      2886 |      12851 | typing
```

Some typing syntax used is technically incorrect for python 3.9, but in order
to correctly type some variables it would require importing typing for that 
python version. To sidestep this, those annotations are currently strings.
This will probably fail to evaluate in 3.9 but this will not be changed.

The `dataclass_transform` decorator is reproduced in `_typing.py` partly to
provide it for python < 3.11 but also because it avoids the slow import from
typing or typing_extensions.
