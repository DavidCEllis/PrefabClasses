# Modified from https://github.com/dabeaz/cluegen/blob/master/perf.py
# A import performance test of:
# standard classes, namedtuple, NamedTuple,
# dataclasses, attrs,
# cluegen, dataklasses,
# prefab and compiled_prefab

import os
import sys
import time
import platform

import prefab_classes


compiled_prefab_template = '''
@prefab(compile_prefab=True)
class C{n}:
    a: int
    b: int
    c: int
    d: int
    e: int

C{n}.__init__, C{n}.__repr__, C{n}.__eq__
'''


def run_test(name, n):
    start = time.time()
    while n > 0:
        if 'compiled' in name:
            from prefab_classes.compiled import prefab_compiler
            with prefab_compiler():
                import perftemp
        else:
            import perftemp
        del sys.modules['perftemp']
        # Delete the cached .pyc file
        perftemp_pyc = getattr(perftemp, "__cached__")
        if perftemp_pyc:
            try:
                os.remove(perftemp_pyc)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Could not delete performance {perftemp_pyc=} "
                    f"as it was not generated"
                )
        n -= 1
    end = time.time()
    print(f"| {name} | {end - start:.2f} |")


def write_perftemp(count, template, setup):
    with open('../perf/perftemp.py', 'w') as f:
        f.write(setup)
        for n in range(count):
            f.write(template.format(n=n))


def main(reps):
    """

    :param reps: Number of repeat imports
    :return:
    """
    print(f"Python Version: {sys.version}")
    print(f"Prefab Classes version: {prefab_classes.__version__}")
    print(f"Platform: {platform.platform()}")

    print(f"Time for {reps} imports of 100 classes defined with 5 basic attributes")
    print("| Method | Total Time (seconds) |")
    print("| --- | --- |")

    compiled_prefab_import = "# COMPILE_PREFABS\n" \
                             "from prefab_classes import prefab\n"

    write_perftemp(100, compiled_prefab_template, compiled_prefab_import)
    run_test(f'compiled_prefab_nocache {prefab_classes.__version__}', reps)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        reps = int(sys.argv[1])
    else:
        reps = 100
    main(reps)
