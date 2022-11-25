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


# Windows Desktop #
Intel(R) Core(TM) i7-4790K CPU @ 4.00GHz / 16GB 1867 MHz DDR3

```
Python Version 3.11.0 (main, Oct 24 2022, 18:26:48) [MSC v.1933 64 bit (AMD64)]
Platform: Windows-10-10.0.19044-SP0
Initial compilation time EXCLUDED
Time for 100 imports of 100 classes defined with 5 basic attributes
```

| Method | Total Time (seconds) |
| --- | --- |
| standard classes | 0.16 |
| namedtuple | 0.64 |
| NamedTuple | 1.05 |
| dataclasses | 3.60 |
| attrs | 5.45 |
| pydantic | 5.05 |
| dabeaz/cluegen | 0.18 |
| dabeaz/cluegen_eval | 1.94 |
| dabeaz/dataklasses | 0.21 |
| dabeaz/dataklasses_eval | 0.21 |
| prefab | 0.27 |
| prefab_eval | 2.12 |
| compiled_prefab | 0.17 |
