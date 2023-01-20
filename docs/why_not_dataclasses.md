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
`python -X importtime -c "import <module>"`. In these examples I have
excluded the `site` import time (which is always imported by python 
unless specifically excluded) and used the best result of 5 (after warmup).

**NOTE: Having some packages installed can change the result so it is best to do
these tests with a clean python environment. For example having `sphinx` installed
will cause `site` to import importlib and hide some of the difference.**

### prefab_classes importtime ###

`python -X importtime -c "import prefab_classes"`

```
import time: self [us] | cumulative | imported package
import time:       142 |        142 |       prefab_classes._typing
import time:       166 |        166 |         prefab_classes.sentinels
import time:       173 |        173 |         prefab_classes.exceptions
import time:       238 |        575 |       prefab_classes.dynamic._attribute_class
import time:       163 |        163 |       prefab_classes.constants
import time:       126 |        126 |         prefab_classes.dynamic.autogen
import time:       296 |        422 |       prefab_classes.dynamic.method_generators
import time:       394 |       1694 |     prefab_classes.dynamic.prefab
import time:       223 |       1917 |   prefab_classes.dynamic
import time:       287 |       2203 | prefab_classes
```

### dataclasses importtime ###

`python -X importtime -c "import dataclasses"`

```
import time: self [us] | cumulative | imported package
import time:       368 |        368 |       types
import time:        81 |         81 |         _operator
import time:       451 |        532 |       operator
import time:       125 |        125 |           itertools
import time:       276 |        276 |           keyword
import time:       282 |        282 |           reprlib
import time:        68 |         68 |           _collections
import time:      1199 |       1949 |         collections
import time:        56 |         56 |         _functools
import time:       747 |       2750 |       functools
import time:      2440 |       6089 |     enum
import time:        74 |         74 |       _sre
import time:      1005 |       1005 |         re._constants
import time:       404 |       1408 |       re._parser
import time:       172 |        172 |       re._casefix
import time:       536 |       2189 |     re._compiler
import time:       299 |        299 |     copyreg
import time:       644 |       9218 |   re
import time:       259 |        259 |       _weakrefset
import time:       552 |        811 |     weakref
import time:       109 |        109 |         org
import time:        14 |        123 |       org.python
import time:        15 |        137 |     org.python.core
import time:       308 |       1255 |   copy
import time:      1049 |       1049 |       _ast
import time:       681 |        681 |       contextlib
import time:      1140 |       2869 |     ast
import time:       364 |        364 |         _opcode
import time:       449 |        813 |       opcode
import time:      1128 |       1941 |     dis
import time:       240 |        240 |     collections.abc
import time:       516 |        516 |         warnings
import time:       258 |        774 |       importlib
import time:        60 |        833 |     importlib.machinery
import time:       235 |        235 |         token
import time:       949 |       1184 |       tokenize
import time:       321 |       1504 |     linecache
import time:      1723 |       9107 |   inspect
import time:       940 |      20519 | dataclasses
```

~8x longer than `prefab_classes`

### attrs importtime ###

```
import time: self [us] | cumulative | imported package
import time:       517 |        517 |     warnings
import time:       103 |        103 |         itertools
import time:       218 |        218 |         keyword
import time:        91 |         91 |           _operator
import time:       469 |        559 |         operator
import time:       276 |        276 |         reprlib
import time:        70 |         70 |         _collections
import time:      1092 |       2317 |       collections
import time:       348 |        348 |       types
import time:        57 |         57 |       _functools
import time:       677 |       3398 |     functools
import time:       267 |        267 |         collections.abc
import time:       649 |        649 |         contextlib
import time:      2920 |       2920 |           enum
import time:       181 |        181 |             _sre
import time:       326 |        326 |               re._constants
import time:       409 |        734 |             re._parser
import time:       186 |        186 |             re._casefix
import time:       506 |       1605 |           re._compiler
import time:       238 |        238 |           copyreg
import time:       595 |       5357 |         re
import time:       354 |        354 |         _typing
import time:      2726 |       9352 |       typing
import time:      1056 |       1056 |             _ast
import time:      1194 |       2250 |           ast
import time:       449 |        449 |               _opcode
import time:       697 |       1145 |             opcode
import time:      1159 |       2304 |           dis
import time:       316 |        316 |             importlib
import time:        89 |        405 |           importlib.machinery
import time:       303 |        303 |               token
import time:      1255 |       1558 |             tokenize
import time:       334 |       1891 |           linecache
import time:      1942 |       8790 |         inspect
import time:      2213 |       2213 |         platform
import time:       376 |        376 |           _weakrefset
import time:      1256 |       1631 |         threading
import time:       383 |      13016 |       attr._compat
import time:       500 |        500 |           weakref
import time:       118 |        118 |               org
import time:       106 |        223 |             org.python
import time:        15 |        238 |           org.python.core
import time:       607 |       1345 |         copy
import time:       126 |        126 |         attr._config
import time:       244 |        244 |           attr.exceptions
import time:       137 |        380 |         attr.setters
import time:      3340 |       5190 |       attr._make
import time:       315 |      27871 |     attr.converters
import time:       167 |        167 |     attr.filters
import time:      6157 |       6157 |     attr.validators
import time:       205 |        205 |     attr._cmp
import time:       185 |        185 |     attr._funcs
import time:       177 |        177 |     attr._next_gen
import time:       741 |        741 |     attr._version_info
import time:       392 |      39805 |   attr
import time:       230 |        230 |   attrs.converters
import time:       114 |        114 |   attrs.exceptions
import time:       152 |        152 |   attrs.filters
import time:       106 |        106 |   attrs.setters
import time:       106 |        106 |   attrs.validators
import time:       575 |      41087 | attrs
```

~16x longer than `prefab_classes`

## Are you just delaying the imports so a bunch will hit at runtime? ##

Generally no, but in certain situations yes.

If you're just making classes and using the dynamic form of prefab
then no extra imports will happen at runtime.

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

## Why not make the compiled method operate on @dataclass ##

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