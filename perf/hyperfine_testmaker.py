"""
This script makes all of the hyperfine tests used in this project
"""

from pathlib import Path
from prefab_classes import prefab

base_dir = Path(__file__).parent / 'hyperfine_testfiles'
importer_dir = base_dir / 'hyperfine_importers'
classdef_dir = importer_dir / 'class_definitions'
results_dir = base_dir / 'hyperfine_results'

# Template Body Files #

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

prefab_attribute_template = '''
@prefab
class C{n}:
    a = attribute()
    b = attribute()
    c = attribute()
    d = attribute()
    e = attribute()
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

# Import Headings #

namedtuple_header = "from collections import namedtuple"
NamedTuple_header = "from typing import NamedTuple"
dataclass_header = "from dataclasses import dataclass"
attr_header = "from attrs import define"
pydantic_header = "from pydantic import BaseModel"
cluegen_header = "from cluegen import Datum"
dataklass_header = "from dataklasses import dataklass"
prefab_header = "from prefab_classes import prefab, attribute"
compiled_prefab_header = "# COMPILE_PREFABS\nfrom prefab_classes import prefab, attribute"


def write_perf_file(outpath, count, template, setup):
    with open(outpath, 'w') as f:
        f.write(setup)
        for n in range(count):
            f.write(template.format(n=n))


@prefab
class TestData:
    import_name: str
    import_header: str
    class_template: str
    use_compile_importer: bool = False
    precompile_prefab: bool = False

    @property
    def importer_file(self):
        importer_name = f"{self.import_name}_timer.py"
        return importer_dir / importer_name

    @property
    def def_file(self):
        def_name = f"{self.import_name}_data.py"
        return classdef_dir / def_name

    def write_perf_importer(self):
        if self.use_compile_importer:
            data = (
                f"from prefab_classes_hook import prefab_compiler\n"
                f"with prefab_compiler():\n"
                f"    import class_definitions.{self.import_name}_data\n"
            )
        else:
            data = f"import class_definitions.{self.import_name}_data\n"
        self.importer_file.write_text(data)

    def write_classdef_file(self, count=100):
        if self.precompile_prefab:
            from prefab_classes.compiled import rewrite_to_py
            tmpdef = self.def_file.with_suffix('.temp')
            with tmpdef.open(mode='w') as f:
                f.write(self.import_header)
                for n in range(count):
                    f.write(self.class_template.format(n=n))

            rewrite_to_py(tmpdef, self.def_file)

            tmpdef.unlink()

        else:
            with self.def_file.open(mode='w') as f:
                f.write(self.import_header)
                for n in range(count):
                    f.write(self.class_template.format(n=n))


datasets = [
    TestData('native_classes', '', standard_template),
    TestData('namedtuples', namedtuple_header, namedtuple_template),
    TestData('typed_namedtuples', NamedTuple_header, NamedTuple_template),
    TestData('dataclasses', dataclass_header, dataclass_template),
    TestData('attrs', attr_header, attr_template),
    TestData('pydantic', pydantic_header, pydantic_template),
    # TestData('cluegen', cluegen_header, cluegen_template),
    # TestData('cluegen_eval', cluegen_header, cluegen_eval_template),
    TestData('prefab_classes', prefab_header, prefab_template),
    TestData('prefab_eval', prefab_header, prefab_eval_template),
    TestData('compiled_prefab', compiled_prefab_header, compiled_prefab_template, use_compile_importer=True),
    TestData('precompiled_prefab', compiled_prefab_header, compiled_prefab_template, precompile_prefab=True),
]


def write_tests(*, runs=100, includes_pass=True):
    base_dir.mkdir(exist_ok=True)
    importer_dir.mkdir(exist_ok=True)
    classdef_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)

    for data in datasets:
        data.write_perf_importer()
        data.write_classdef_file(count=100)

    tests = " ".join(
        f"'python hyperfine_importers/{data.import_name}_timer.py'"
        for data in datasets
    )

    versions = (
        "import attrs, pydantic, prefab_classes;"
        "print(f'attrs {attrs.__version__}');"
        "print(f'pydantic {pydantic.__version__}');"
        "print(f'prefab_classes {prefab_classes.__version__}\\n')"
    )

    if includes_pass:
        tests = f"'python -c \"pass\"' {tests}"

    outpath = results_dir / 'hyperfine_result.md'

    zsh_script = (
        "python -VV\n"
        f"python -c \"{versions}\"\n"
        f"hyperfine --export-markdown {outpath} --shell=none --runs {runs} --warmup 10 {tests}"
    )

    shell_pth = base_dir / "hyperfine_runner.sh"
    shell_pth.write_text(zsh_script)

    outpath = results_dir / 'hyperfine_importtimes.md'

    tests = (
        """'python -c "pass"' """
        """'python -c "import collections"' """
        """'python -c "import typing"' """
        """'python -c "import dataclasses"' """
        """'python -c "import attrs"' """
        """'python -c "import pydantic"' """
        """'python -c "import prefab_classes"' """
    )

    import_script = (
        f"hyperfine --export-markdown {outpath} --shell=none --runs {runs} --warmup 10 {tests}"
    )

    shell_pth = base_dir / 'hyperfine_importtimes.sh'
    shell_pth.write_text(import_script)


if __name__ == '__main__':
    write_tests(includes_pass=True)
