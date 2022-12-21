# perf.py results #

These are the results from running perf.py on different machines I have access to.

This is **NOT** an overall performance test. This is just intended to check - 
very roughly - how quickly a module with a large number of generated classes 
will import.

These test results do not include the time for the initial .pyc compilation of the
test file.

## 2018 Macbook Pro ##

2.3 GHz Quad-Core Intel Core i5 / 8 GB 2133 MHz LPDDR3

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