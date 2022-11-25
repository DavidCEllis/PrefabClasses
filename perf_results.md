# perf.py results #

These are the results from running perf.py on different machines I have access to.

This is **NOT** an overall performance test. This is just intended to check how
quickly a module with a large number of generated classes will import.

These test results do not include the time for the initial .pyc compilation of the
test file.

## 2018 Macbook Pro ##

2.3 GHz Quad-Core Intel Core i5 / 8 GB 2133 MHz LPDDR3

```
Python Version 3.11.0 (main, Oct 26 2022, 01:05:56) [Clang 13.0.0 (clang-1300.0.29.30)]
Platform: macOS-12.6-x86_64-i386-64bit
Initial compilation time EXCLUDED
Time for 100 imports of 100 classes defined with 5 basic attributes
```

| Method | Total Time (seconds) |
| --- | --- |
| standard classes | 0.15 |
| namedtuple | 0.75 |
| NamedTuple | 1.32 |
| dataclasses | 4.21 |
| attrs | 6.44 |
| pydantic | 5.71 |
| dabeaz/cluegen | 0.19 |
| dabeaz/cluegen_eval | 2.25 |
| dabeaz/dataklasses | 0.22 |
| dabeaz/dataklasses_eval | 0.21 |
| prefab | 0.29 |
| prefab_eval | 2.51 |
| compiled_prefab | 0.16 |

