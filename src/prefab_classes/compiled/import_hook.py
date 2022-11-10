"""
Hook into the import mechanism and sneakily translate our modules before python gets there
"""
import sys

from importlib.machinery import PathFinder, SourceFileLoader
from importlib.util import decode_source


HOOK_REWRITE = '#COMPILE_PREFABS'


def check_parse(module_path):
    """
    Check if a module should be parsed for prefab

    Looks a the start of the file through comments, if HOOK_REWRITE is found
    returns True, otherwise returns False after getting through the comments.
    """
    parse_module = False
    try:
        with open(module_path, 'r') as f:
            for line in f:
                if line[0] != '#':
                    break
                elif line.strip() == HOOK_REWRITE:
                    parse_module = True
                    break
    except UnicodeError:
        pass
    return parse_module


# noinspection PyMethodOverriding,PyArgumentList
class PrefabHacker(SourceFileLoader):
    def __getattribute__(self, item):
        # print(item)
        return super().__getattribute__(item)

    def source_to_code(self, data, path, *, _optimize=-1):
        # Only import the generator code if it is actually going to be used
        from .generator import generate_prefabs

        sys.stderr.write(f'Prefab Converted File: {path}\n')
        src = decode_source(data)
        prefab_src = generate_prefabs(src)
        return super().source_to_code(prefab_src, path, _optimize=_optimize)


class PrefabFinder(PathFinder):
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path, target)
        origin = getattr(spec, 'origin', None)
        if origin and check_parse(origin):
            new_loader = PrefabHacker(spec.loader.name, spec.loader.path)
            spec.loader = new_loader
            return spec
        return None


def insert_prefab_importhook():
    """
    Add the prefab import hook to sys.meta_path
    :return:
    """
    index = 0
    for i, finder in enumerate(sys.meta_path):
        finder = finder if type(finder) is type else type(finder)
        if issubclass(finder, PathFinder):
            index = i
            break

    # Make PrefabFinder the first importer before other PathFinders
    sys.meta_path.insert(index, PrefabFinder)
