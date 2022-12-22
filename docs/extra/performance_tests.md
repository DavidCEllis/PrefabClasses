# Performance test results #

All of these tests are run on the 2018 Macbook Pro I've been using for development
unless otherwise mentioned.

Macbook: 2.3 GHz Quad-Core Intel Core i5 / 8 GB 2133 MHz LPDDR3

## Hyperfine tests ##

This is a series of tests of the time it takes to launch python and generate 100
classes each with 5 attributes. 

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

Development Mac
```
Python 3.11.1 (main, Dec  7 2022, 05:32:48) [Clang 13.0.0 (clang-1300.0.29.30)]
attrs 22.2.0
pydantic 1.10.2
prefab_classes v0.7.8a1

Benchmark 1: python -c "pass"
  Time (mean ± σ):      24.5 ms ±   0.6 ms    [User: 15.8 ms, System: 6.0 ms]
  Range (min … max):    23.4 ms …  26.7 ms    100 runs
 
Benchmark 2: python hyperfine_importers/native_classes_timer.py
  Time (mean ± σ):      25.7 ms ±   1.0 ms    [User: 16.6 ms, System: 6.3 ms]
  Range (min … max):    24.1 ms …  30.3 ms    100 runs
 
Benchmark 3: python hyperfine_importers/namedtuples_timer.py
  Time (mean ± σ):      33.3 ms ±   0.6 ms    [User: 23.7 ms, System: 6.5 ms]
  Range (min … max):    32.4 ms …  35.7 ms    100 runs
 
Benchmark 4: python hyperfine_importers/typed_namedtuples_timer.py
  Time (mean ± σ):      47.8 ms ±   1.5 ms    [User: 36.5 ms, System: 8.2 ms]
  Range (min … max):    45.2 ms …  53.9 ms    100 runs
 
Benchmark 5: python hyperfine_importers/dataclasses_timer.py
  Time (mean ± σ):      82.2 ms ±   1.7 ms    [User: 69.6 ms, System: 9.4 ms]
  Range (min … max):    80.5 ms …  91.8 ms    100 runs
 
Benchmark 6: python hyperfine_importers/attrs_timer.py
  Time (mean ± σ):     123.4 ms ±   1.8 ms    [User: 109.3 ms, System: 11.1 ms]
  Range (min … max):   120.5 ms … 132.9 ms    100 runs
 
Benchmark 7: python hyperfine_importers/pydantic_timer.py
  Time (mean ± σ):     140.2 ms ±   1.2 ms    [User: 120.6 ms, System: 16.2 ms]
  Range (min … max):   137.3 ms … 146.0 ms    100 runs
 
Benchmark 8: python hyperfine_importers/prefab_classes_timer.py
  Time (mean ± σ):      29.9 ms ±   1.6 ms    [User: 20.3 ms, System: 6.7 ms]
  Range (min … max):    28.0 ms …  38.2 ms    100 runs
 
Benchmark 9: python hyperfine_importers/prefab_eval_timer.py
  Time (mean ± σ):      51.6 ms ±   1.1 ms    [User: 41.9 ms, System: 6.7 ms]
  Range (min … max):    49.6 ms …  54.6 ms    100 runs
 
Benchmark 10: python hyperfine_importers/compiled_prefab_timer.py
  Time (mean ± σ):      29.3 ms ±   1.4 ms    [User: 19.4 ms, System: 7.0 ms]
  Range (min … max):    27.5 ms …  33.3 ms    100 runs
 
Benchmark 11: python hyperfine_importers/precompiled_prefab_timer.py
  Time (mean ± σ):      25.3 ms ±   0.8 ms    [User: 16.4 ms, System: 6.0 ms]
  Range (min … max):    24.2 ms …  27.5 ms    100 runs
 
Summary
  'python -c "pass"' ran
    1.03 ± 0.04 times faster than 'python hyperfine_importers/precompiled_prefab_timer.py'
    1.05 ± 0.05 times faster than 'python hyperfine_importers/native_classes_timer.py'
    1.20 ± 0.07 times faster than 'python hyperfine_importers/compiled_prefab_timer.py'
    1.22 ± 0.07 times faster than 'python hyperfine_importers/prefab_classes_timer.py'
    1.36 ± 0.04 times faster than 'python hyperfine_importers/namedtuples_timer.py'
    1.95 ± 0.08 times faster than 'python hyperfine_importers/typed_namedtuples_timer.py'
    2.10 ± 0.07 times faster than 'python hyperfine_importers/prefab_eval_timer.py'
    3.35 ± 0.11 times faster than 'python hyperfine_importers/dataclasses_timer.py'
    5.03 ± 0.15 times faster than 'python hyperfine_importers/attrs_timer.py'
    5.71 ± 0.16 times faster than 'python hyperfine_importers/pydantic_timer.py'
```

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
