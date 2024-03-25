# Why make this when we have dataclasses/attrs #

The core goal behind this project is to impose as little penalty as possible at runtime
to writing classes as prefabs vs writing the whole class out by hand.

This is not the case for any of the current implementations as dataclasses/attrs/pydantic
classes impose a performance penalty for generating the classes over writing the class by
hand.

`prefab_classes` aims to minimise this penalty as much as possible and in some cases
remove it altogether.

## Import Performance ##

There have been 
[some](https://github.com/python-attrs/attrs/issues/575) 
[discussions](https://discuss.python.org/t/improving-dataclasses-startup-performance/15442)
and
[comments](https://github.com/dabeaz/cluegen#wait-hasnt-this-already-been-invented)
about the performance on import of code generators like dataclasses and attrs.

Part of this that seems to be ignored is the time spent importing other modules
on load. It's possible to see the impact of this by looking at importtime using 
`python -X importtime -c "from <module> import <method>"`. In these examples I have
excluded the `site` import time (which is always imported by python 
unless specifically excluded) and used the best result of 5 (after warmup).

**NOTE: Having some packages installed can change the result so it is best to do
these tests with a clean python environment. For example having `sphinx` installed
will cause `site` to import importlib and hide some of the difference.**

### prefab_classes importtime ###

`python -X importtime -c "from prefab_classes import prefab"`

```
import time: self [us] | cumulative | imported package
import time:       303 |        303 |     ducktools
import time:       519 |        821 |   ducktools.lazyimporter
import time:       544 |       1365 | prefab_classes
import time:       382 |        382 |     warnings
import time:       195 |        195 |     prefab_classes.shared
import time:       270 |        270 |     prefab_classes.dynamic.method_generators
import time:       492 |       1338 |   prefab_classes.dynamic.prefab
import time:       337 |       1674 | prefab_classes.dynamic
```

### dataclasses importtime ###

`python -X importtime -c "from dataclasses import dataclass"`

```
import time: self [us] | cumulative | imported package
import time:       377 |        377 |       types
import time:        47 |         47 |         _operator
import time:       470 |        516 |       operator
import time:       115 |        115 |           itertools
import time:       256 |        256 |           keyword
import time:       281 |        281 |           reprlib
import time:        49 |         49 |           _collections
import time:       869 |       1568 |         collections
import time:        38 |         38 |         _functools
import time:       651 |       2257 |       functools
import time:      1094 |       4242 |     enum
import time:        53 |         53 |       _sre
import time:       303 |        303 |         re._constants
import time:       559 |        861 |       re._parser
import time:       212 |        212 |       re._casefix
import time:       772 |       1896 |     re._compiler
import time:       284 |        284 |     copyreg
import time:       932 |       7353 |   re
import time:       340 |        340 |       _weakrefset
import time:       569 |        909 |     weakref
import time:       399 |       1307 |   copy
import time:       542 |        542 |       _ast
import time:       631 |        631 |       contextlib
import time:      1544 |       2717 |     ast
import time:        27 |         27 |         _opcode
import time:       504 |        530 |       opcode
import time:       761 |       1291 |     dis
import time:       294 |        294 |     collections.abc
import time:       388 |        388 |         warnings
import time:       347 |        734 |       importlib
import time:        89 |        822 |     importlib.machinery
import time:       261 |        261 |         token
import time:        30 |         30 |         _tokenize
import time:       822 |       1113 |       tokenize
import time:       332 |       1444 |     linecache
import time:      1776 |       8341 |   inspect
import time:       854 |      17853 | dataclasses
```


### attrs importtime ###

`from attrs import define`

```
import time: self [us] | cumulative | imported package
import time:       117 |        117 |         itertools
import time:       303 |        303 |         keyword
import time:        47 |         47 |           _operator
import time:       438 |        484 |         operator
import time:       308 |        308 |         reprlib
import time:        49 |         49 |         _collections
import time:      1218 |       2477 |       collections
import time:       453 |        453 |       types
import time:        56 |         56 |       _functools
import time:       966 |       3951 |     functools
import time:       351 |        351 |       collections.abc
import time:       406 |        406 |       copyreg
import time:       633 |        633 |       contextlib
import time:      1084 |       1084 |         enum
import time:        69 |         69 |           _sre
import time:       477 |        477 |             re._constants
import time:       632 |       1109 |           re._parser
import time:       267 |        267 |           re._casefix
import time:       934 |       2377 |         re._compiler
import time:       746 |       4206 |       re
import time:       409 |        409 |       warnings
import time:        29 |         29 |       _typing
import time:      2105 |       8135 |     typing
import time:       541 |        541 |             _ast
import time:      1132 |       1672 |           ast
import time:        28 |         28 |               _opcode
import time:       527 |        554 |             opcode
import time:       843 |       1397 |           dis
import time:       357 |        357 |             importlib
import time:       113 |        470 |           importlib.machinery
import time:       285 |        285 |               token
import time:        25 |         25 |               _tokenize
import time:       842 |       1151 |             tokenize
import time:       368 |       1519 |           linecache
import time:      2420 |       7475 |         inspect
import time:      1701 |       1701 |           _wmi
import time:       860 |       2561 |         platform
import time:       665 |        665 |           _weakrefset
import time:      1118 |       1783 |         threading
import time:       749 |      12566 |       attr._compat
import time:       549 |        549 |           weakref
import time:       425 |        974 |         copy
import time:       170 |        170 |         attr._config
import time:       278 |        278 |             __future__
import time:       278 |        555 |           attr.exceptions
import time:       221 |        776 |         attr.setters
import time:      2072 |       3990 |       attr._make
import time:       493 |      17048 |     attr.converters
import time:       345 |        345 |     attr.filters
import time:      3678 |       3678 |     attr.validators
import time:       303 |        303 |     attr._cmp
import time:       223 |        223 |     attr._funcs
import time:       184 |        184 |     attr._next_gen
import time:       590 |        590 |     attr._version_info
import time:      1445 |      35899 |   attr
import time:       264 |        264 |   attrs.converters
import time:       147 |        147 |   attrs.exceptions
import time:       130 |        130 |   attrs.filters
import time:       122 |        122 |   attrs.setters
import time:       125 |        125 |   attrs.validators
import time:       885 |      37571 | attrs
```

~16x longer than `prefab_classes`

## Are you just delaying the imports so a bunch will hit at runtime? ##

Yes and no.

Prefab Classes does make use of deferred imports internally. However by importing
`prefab` here the basic modules needed are imported.

If you're just making classes and using the dynamic form of prefab
then no other extra imports will happen at runtime.

If you want to export `json` the `funcs` module will only import stdlib
`json` when `to_json` is called and if a third party dumps function 
(such as the one from orjson) is not provided.

When making compiled prefabs the first time a module is imported and the
.pyc file is generated, extra modules are needed to perform the compilation
and will be imported then. Once the .pyc is made, the next import they will
not be needed and so are not imported.

The methods for rewriting to source import some modules on first use, this
is simply so they can be available more easily without having a major hit on
performance if they are not used.

## What about when generating classes ##

For full performance tests on class generation, check {doc}`extra/performance_tests`
