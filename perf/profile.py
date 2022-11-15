# Modified from https://github.com/dabeaz/cluegen/blob/master/perf.py
# A import performance test of:
# standard classes, namedtuple, NamedTuple,
# dataclasses, attrs,
# cluegen, dataklasses,
# prefab and compiled_prefab

import sys
import time

# Import everything here, prefab_classes has to be imported already for compilation to work.
# To avoid the potential for unfairness import everything here.
from collections import namedtuple
from typing import NamedTuple

try:
    import attrs
except ImportError:
    pass
try:
    import pydantic
except ImportError:
    pass

import dataclasses
import cluegen
import dataklasses
import prefab_classes

standard_template = '''
class C{n}:
    def __init__(self, a, b, c, d, e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def __repr__(self):
        return f'C{n}({{self.a!r}}, {{self.b!r}}, {{self.c!r}}, {{self.d!r}}, {{self.e!r}})'

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return (self.a, self.b, self.c, self.d, self.e) == (other.a, other.b, other.c, other.d, other.e)
        else:
            return NotImplemented
'''

namedtuple_template = '''
C{n} = namedtuple('C{n}', ['a', 'b', 'c', 'd', 'e'])
'''

NamedTuple_template = '''
class C{n}(NamedTuple):
    a : int
    b : int
    c : int
    d : int
    e : int
'''

dataclass_template = '''
@dataclass
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int
'''

attr_template = '''
@define
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int
'''

pydantic_template = '''
class C{n}(BaseModel):
    a: int
    b: int
    c: int
    d: int
    e: int
'''

cluegen_template = '''
class C{n}(Datum):
    a: int
    b: int
    c: int
    d: int
    e: int
'''

# cluegen, but same default methods as dataclasses generated
cluegen_eval_template = '''
class C{n}(Datum):
    a: int
    b: int
    c: int
    d: int
    e: int

C{n}.__init__, C{n}.__repr__, C{n}.__eq__
'''

dataklass_template = '''
@dataklass
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int
'''


dataklass_eval_template = '''
@dataklass
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int
    
C{n}.__init__, C{n}.__repr__, C{n}.__eq__
'''

prefab_template = '''
@prefab
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int
'''

prefab_eval_template = '''
@prefab
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int

C{n}.__init__, C{n}.__repr__, C{n}.__eq__
'''

compiled_prefab_template = '''
@prefab(compile_prefab=True)
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int
'''

compiled_plain_template = '''
@prefab(compile_prefab=True, compile_plain=True)
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int
'''


def run_test(name, n, exclude_compile=False):
    if exclude_compile:
        if 'compiled' in name:
            from prefab_classes import prefab_compiler
            with prefab_compiler():
                import perftemp
        else:
            import perftemp
        del sys.modules['perftemp']

    start = time.time()
    while n > 0:
        if 'compiled' in name:
            from prefab_classes import prefab_compiler
            with prefab_compiler():
                import perftemp
        else:
            import perftemp
        del sys.modules['perftemp']
        n -= 1
    end = time.time()
    print(name, (end - start))


def write_perftemp(count, template, setup):
    with open('../perf/perftemp.py', 'w') as f:
        f.write(setup)
        for n in range(count):
            f.write(template.format(n=n))


def main(reps, test_everything=False, exclude_compile=False):
    write_perftemp(100, standard_template, '')
    run_test('standard classes', reps, exclude_compile=exclude_compile)

    if test_everything:
        write_perftemp(100, namedtuple_template, 'from collections import namedtuple\n')
        run_test('namedtuple', reps, exclude_compile=exclude_compile)

        write_perftemp(100, NamedTuple_template, 'from typing import NamedTuple\n')
        run_test('NamedTuple', reps, exclude_compile=exclude_compile)

        write_perftemp(100, dataclass_template, 'from dataclasses import dataclass\n')
        run_test('dataclasses', reps, exclude_compile=exclude_compile)

        try:
            write_perftemp(100, attr_template, 'from attrs import define\n')
            run_test('attrs', reps, exclude_compile=exclude_compile)
        except ImportError:
            print("attrs not installed")

        try:
            write_perftemp(100, pydantic_template, 'from pydantic import BaseModel\n')
            run_test('pydantic', reps, exclude_compile=exclude_compile)
        except ImportError:
            print("pydantic not installed")

        write_perftemp(100, cluegen_template, 'from cluegen import Datum\n')
        run_test('cluegen', reps, exclude_compile=exclude_compile)

        write_perftemp(100, cluegen_eval_template, 'from cluegen import Datum\n')
        run_test('cluegen_eval', reps, exclude_compile=exclude_compile)

        write_perftemp(100, dataklass_template, 'from dataklasses import dataklass\n')
        run_test('dataklasses', reps, exclude_compile=exclude_compile)

        write_perftemp(100, dataklass_eval_template, 'from dataklasses import dataklass\n')
        run_test('dataklasses_eval', reps, exclude_compile=exclude_compile)

    prefab_import = "from prefab_classes import prefab, attribute\n" \
                    "from prefab_classes.register import prefab_register\n" \
                    "prefab_register.clear()\n"

    write_perftemp(100, prefab_template, prefab_import)
    run_test('prefab', reps, exclude_compile=exclude_compile)

    write_perftemp(100, prefab_eval_template, prefab_import)
    run_test('prefab_eval', reps, exclude_compile=exclude_compile)

    compiled_prefab_import = "# COMPILE_PREFABS\n" \
                             "from prefab_classes import prefab\n" \
                             "from prefab_classes.register import prefab_register\n" \
                             "prefab_register.clear()\n"

    write_perftemp(100, compiled_prefab_template, compiled_prefab_import)
    run_test('compiled_prefab', reps, exclude_compile=exclude_compile)

    write_perftemp(100, compiled_plain_template, compiled_prefab_import)
    run_test('compiled_prefab_plain', reps, exclude_compile=exclude_compile)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        reps = int(sys.argv[1])
    else:
        reps = 100
    main(reps, test_everything=True, exclude_compile=True)