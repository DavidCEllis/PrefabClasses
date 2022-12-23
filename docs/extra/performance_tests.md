# Performance test results #

Tests are run on 2 different machines.

Rough specs:
XPS 13 9360 Laptop: Ubuntu 20.04 / Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz / 16 GB 1867MHz LPDDR3
2018 Macbook: MacOS 12.6 / 2.3 GHz Quad-Core Intel Core i5 / 8 GB 2133 MHz LPDDR3

## Hyperfine tests ##

### Import Time ###

This just tests the overall time to launch python and import the module to be used 
for constructing classes. `python -c "pass"` used as a baseline.

#### XPS 13 ####



### Class Contruction ###

This is a series of tests of the time it takes to launch python and generate 100
classes each with 5 attributes.

The code for each class looks roughly like this:

```python
@dataclass
class C0:
    a: int
    b: int
    c: int
    d: int
    e: int
```

In some cases the `__init__`, `__repr__` and `__eq__` functions are also looked up
in order to force them to be generated (prefab_eval).

For a baseline comparison, `python -c "pass"` is included just to show the overhead
from the interpreter.

As `prefab_classes` has multiple ways of generating classes it is here multiple times.

`prefab_classes_timer` generates the classes dynamically, but leaves the methods 
unused so they are not yet evaluated. This is how they would usually be on import.

`prefab_eval_timer` generates the classes dynamically, and also generates their 
methods as they would be after first use.

`compiled_prefab_timer` uses compiled classes in the .pyc files via the import
hook. This has some overhead from hashed .pyc validation and additional imports.

`precompiled_prefab_timer` uses classes that have been rewritten out to .py and so
should be the same speed as regular python classes, as that's what they are.

#### XPS13 ####

```
Python 3.11.1 (main, Dec 22 2022, 12:04:25) [GCC 9.4.0]
attrs 22.2.0
pydantic 1.10.2
prefab_classes v0.7.8a1
```

| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `python -c "pass"` | 11.3 ± 0.3 | 10.9 | 12.0 | 1.00 |
| `python hyperfine_importers/native_classes_timer.py` | 13.2 ± 0.4 | 12.7 | 14.8 | 1.17 ± 0.04 |
| `python hyperfine_importers/namedtuples_timer.py` | 21.7 ± 0.4 | 21.0 | 23.9 | 1.92 ± 0.06 |
| `python hyperfine_importers/typed_namedtuples_timer.py` | 35.9 ± 0.9 | 34.9 | 43.7 | 3.18 ± 0.11 |
| `python hyperfine_importers/dataclasses_timer.py` | 74.1 ± 0.7 | 73.0 | 78.8 | 6.56 ± 0.16 |
| `python hyperfine_importers/attrs_timer.py` | 121.4 ± 1.5 | 119.6 | 128.9 | 10.75 ± 0.28 |
| `python hyperfine_importers/pydantic_timer.py` | 139.1 ± 1.9 | 136.3 | 151.0 | 12.32 ± 0.32 |
| `python hyperfine_importers/prefab_classes_timer.py` | 17.5 ± 0.4 | 17.0 | 19.5 | 1.55 ± 0.05 |
| `python hyperfine_importers/prefab_eval_timer.py` | 44.2 ± 3.7 | 42.4 | 74.1 | 3.91 ± 0.34 |
| `python hyperfine_importers/compiled_prefab_timer.py` | 16.3 ± 0.6 | 15.7 | 20.3 | 1.45 ± 0.06 |
| `python hyperfine_importers/precompiled_prefab_timer.py` | 13.3 ± 0.4 | 12.9 | 14.7 | 1.18 ± 0.04 |


#### Macbook ####

```
Python 3.11.1 (main, Dec  7 2022, 05:32:48) [Clang 13.0.0 (clang-1300.0.29.30)]
attrs 22.2.0
pydantic 1.10.2
prefab_classes v0.7.8a1
```

| Command | Mean [ms] | Min [ms] | Max [ms] | Relative |
|:---|---:|---:|---:|---:|
| `python -c "pass"` | 24.7 ± 1.7 | 22.9 | 32.2 | 1.00 |
| `python hyperfine_importers/native_classes_timer.py` | 25.8 ± 0.8 | 24.7 | 28.0 | 1.04 ± 0.08 |
| `python hyperfine_importers/namedtuples_timer.py` | 34.0 ± 1.5 | 31.9 | 37.5 | 1.37 ± 0.11 |
| `python hyperfine_importers/typed_namedtuples_timer.py` | 48.1 ± 1.9 | 45.4 | 55.9 | 1.95 ± 0.15 |
| `python hyperfine_importers/dataclasses_timer.py` | 81.6 ± 0.8 | 80.6 | 86.4 | 3.30 ± 0.23 |
| `python hyperfine_importers/attrs_timer.py` | 123.2 ± 2.2 | 121.1 | 134.2 | 4.98 ± 0.35 |
| `python hyperfine_importers/pydantic_timer.py` | 141.3 ± 2.0 | 139.1 | 153.5 | 5.71 ± 0.40 |
| `python hyperfine_importers/prefab_classes_timer.py` | 29.8 ± 0.9 | 28.6 | 32.3 | 1.20 ± 0.09 |
| `python hyperfine_importers/prefab_eval_timer.py` | 52.0 ± 1.2 | 50.2 | 58.1 | 2.10 ± 0.15 |
| `python hyperfine_importers/compiled_prefab_timer.py` | 29.1 ± 0.8 | 28.0 | 30.9 | 1.18 ± 0.09 |
| `python hyperfine_importers/precompiled_prefab_timer.py` | 25.8 ± 0.8 | 24.8 | 27.7 | 1.04 ± 0.08 |


## perf_profile.py ##

This is **NOT** an overall performance test. This is just intended to check - 
very roughly - how quickly a module with a large number of generated classes 
will import.

These test results do not include the time for the initial .pyc compilation of the
test file.

These tests are just run on the 2018 Macbook Pro I've been using for development:
2.3 GHz Quad-Core Intel Core i5 / 8 GB 2133 MHz LPDDR3

### v0.7.7 ###

```
Python Version: 3.11.1 (main, Dec  7 2022, 05:32:48) [Clang 13.0.0 (clang-1300.0.29.30)]
Prefab Classes version: v0.7.7
Platform: macOS-12.6-x86_64-i386-64bit
Initial compilation time EXCLUDED
Time for 100 imports of 100 classes defined with 5 basic attributes
```

| Method | Total Time (seconds) |
| --- | --- |
| standard classes | 0.15 |
| namedtuple | 0.76 |
| NamedTuple | 1.25 |
| dataclasses | 3.91 |
| attrs 22.2.0 | 6.40 |
| pydantic 1.10.2 | 5.22 |
| dabeaz/cluegen | 0.17 |
| dabeaz/cluegen_eval | 2.01 |
| dabeaz/dataklasses | 0.19 |
| dabeaz/dataklasses_eval | 0.22 |
| prefab v0.7.7 | 0.33 |
| prefab_attributes v0.7.7 | 0.32 |
| prefab_eval v0.7.7 | 2.59 |
| compiled_prefab v0.7.7 | 0.16 |
| compiled_prefab_nocache v0.7.7 | 7.81 |


### v0.7.5a4 ###

```
Python Version: 3.11.0 (main, Oct 26 2022, 01:05:56) [Clang 13.0.0 (clang-1300.0.29.30)]
Prefab Classes version: v0.7.5a4
Platform: macOS-12.6-x86_64-i386-64bit
Initial compilation time EXCLUDED
Time for 100 imports of 100 classes defined with 5 basic attributes
```

| Method | Total Time (seconds) |
| --- | --- |
| standard classes | 0.15 |
| namedtuple | 0.71 |
| NamedTuple | 1.22 |
| dataclasses | 4.13 |
| attrs 22.1.0 | 6.25 |
| pydantic 1.10.2 | 5.50 |
| dabeaz/cluegen | 0.18 |
| dabeaz/cluegen_eval | 2.19 |
| dabeaz/dataklasses | 0.21 |
| dabeaz/dataklasses_eval | 0.20 |
| prefab v0.7.5a4 | 0.35 |
| prefab_attributes v0.7.5a4 | 0.36 |
| prefab_eval v0.7.5a4 | 2.69 |
| compiled_prefab v0.7.5a4 | 0.16 |
| compiled_prefab_nocache v0.7.5a4 | 8.16 |
