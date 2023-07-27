"""
Hook into the import mechanism and sneakily translate our modules before python gets there
"""
import sys

# We probably shouldn't be importing from here, but it also halves the import time.
try:
    from _frozen_importlib_external import PathFinder, SourceFileLoader  # type: ignore
except ImportError:
    from importlib.machinery import PathFinder, SourceFileLoader

__version__ = "v0.9.3"
PREFAB_MAGIC_BYTES = b"PREFAB_CLASSES_v0.9.3"

__all__ = ["prefab_compiler", "insert_prefab_importhook", "remove_prefab_importhook"]


HOOK_REWRITE = "# COMPILE_PREFABS"


def check_parse(module_path):
    """
    Check if a module should be parsed for prefab

    Looks a the start of the file through comments, if HOOK_REWRITE is found
    returns True, otherwise returns False after getting through the comments.
    """
    parse_module = False
    try:
        with open(module_path, "r") as f:
            for line in f:
                if line[0] != "#":
                    break
                elif line.strip() == HOOK_REWRITE:
                    parse_module = True
                    break
    except (UnicodeError, FileNotFoundError):
        pass
    return parse_module


# noinspection PyMethodOverriding,PyArgumentList
class PrefabHacker(SourceFileLoader):
    def __getattribute__(self, item):
        return super().__getattribute__(item)

    def source_to_code(self, data, path, *, _optimize=-1):
        # Only import the generator code if it is actually going to be used
        from prefab_classes.compiled.generator import compile_prefabs

        # Here we don't mind that importlib.util is slow to import
        # as we only do this on the compiling run
        from importlib.util import decode_source

        src = decode_source(data)
        prefab_src = compile_prefabs(src)

        code = super().source_to_code(prefab_src, path, _optimize=_optimize)
        # sys.stdout.write(f"Prefab Converted File: {path}\n")

        return code

    @staticmethod
    def make_pyc_hash(source_bytes):
        # Modify the data given to the hash with extra data
        hash_input_bytes = b"".join([PREFAB_MAGIC_BYTES, source_bytes])
        try:
            # The fast way
            from _imp import source_hash

            try:
                # Fastest
                from _frozen_importlib_external import _RAW_MAGIC_NUMBER  # type: ignore
            except ImportError:
                # Slightly slower as importlib gets imported
                from importlib._bootstrap_external import _RAW_MAGIC_NUMBER  # type: ignore

            return source_hash(_RAW_MAGIC_NUMBER, hash_input_bytes)
        except ImportError:
            # The "correct"/slow way
            from importlib.util import source_hash

            return source_hash(hash_input_bytes)

    # noinspection PyUnresolvedReferences,PyProtectedMember
    def get_code(self, fullname):
        """
        Modified from SourceLoader.get_code method in _bootstrap_external
        Need the whole function in order to modify the invalidation method.

        For compilation to work correctly this Loader must invalidate .pyc files
        compiled by python's own loader and vice versa. Updates to python and
        updates to the generator must also invalidate .pyc files.

        This works by adding PREFAB_MAGIC_BYTES to the data before the hash is
        generated.

        Concrete implementation of InspectLoader.get_code.
        Reading of bytecode requires path_stats to be implemented. To write
        bytecode, set_data must also be implemented.
        """
        # These imports are all needed just for this function.
        # Unlike most of the other imports I don't know if there's a "right" place
        # to get these from.
        try:
            from _frozen_importlib_external import (
                cache_from_source,
                _classify_pyc,
                _validate_hash_pyc,
                _compile_bytecode,
                _code_to_hash_pyc,
            )
        except ImportError:
            from importlib._bootstrap_external import (
                cache_from_source,
                _classify_pyc,
                _validate_hash_pyc,
                _compile_bytecode,
                _code_to_hash_pyc,
            )

        source_path = self.get_filename(fullname)
        source_bytes = None
        source_hash_data = None
        check_source = True
        try:
            bytecode_path = cache_from_source(source_path)
        except NotImplementedError:
            bytecode_path = None
        else:
            try:
                data = self.get_data(bytecode_path)
            except OSError:
                pass
            else:
                exc_details = {
                    "name": fullname,
                    "path": bytecode_path,
                }
                try:
                    flags = _classify_pyc(data, fullname, exc_details)
                    bytes_data = memoryview(data)[16:]
                    used_hash = flags & 0b1 != 0
                    if used_hash:
                        source_bytes = self.get_data(source_path)
                        source_hash_data = self.make_pyc_hash(source_bytes)
                        _validate_hash_pyc(
                            data, source_hash_data, fullname, exc_details
                        )
                    else:
                        raise ImportError(
                            "Timestamp based .pyc validation is invalid for this loader"
                        )
                except (ImportError, EOFError):
                    pass
                else:
                    return _compile_bytecode(
                        bytes_data,
                        name=fullname,
                        bytecode_path=bytecode_path,
                        source_path=source_path,
                    )

        if source_bytes is None:
            source_bytes = self.get_data(source_path)
        code_object = self.source_to_code(source_bytes, source_path)
        # _bootstrap._verbose_message('code object from {}', source_path)
        if not sys.dont_write_bytecode and bytecode_path is not None:

            if source_hash_data is None:
                source_hash_data = self.make_pyc_hash(source_bytes)

            data = _code_to_hash_pyc(code_object, source_hash_data, check_source)

            try:
                self._cache_bytecode(source_path, bytecode_path, data)
            except NotImplementedError:
                pass
        return code_object


class PrefabFinder(PathFinder):
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path, target)
        origin = getattr(spec, "origin", None)
        if origin and check_parse(origin):
            new_loader = PrefabHacker(spec.loader.name, spec.loader.path)
            spec.loader = new_loader
            return spec
        return None


def insert_prefab_importhook():
    """
    Add the prefab import hook to sys.meta_path
    """
    # Don't insert the prefab finder if it is already in the list
    if PrefabFinder in sys.meta_path:
        return

    index = 0
    for i, finder in enumerate(sys.meta_path):
        finder = finder if type(finder) is type else type(finder)
        if issubclass(finder, PathFinder):
            index = i
            break

    # Make PrefabFinder the first importer before other PathFinders
    sys.meta_path.insert(index, PrefabFinder)


def remove_prefab_importhook():
    """
    Remove the prefab import hook from sys.meta_path
    """
    try:
        sys.meta_path.remove(PrefabFinder)
    except ValueError:  # PrefabFinder not in the list
        pass


class prefab_compiler:
    """
    Context manager to insert and clean up the prefab compilation import hook.

    This function should be used before importing any modules with prefabs
    you wish to be compiled. These modules will then be converted to .pyc files
    with a special identifier so they will only be re-converted if a change is
    made to the .py file, if there is a new version of prefab_classes or if
    there is a new python magic number.

    usage::

        with prefab_compiler():
            import my_prefab_module
    """

    def __enter__(self):
        insert_prefab_importhook()

    def __exit__(self, exc_type, exc_val, exc_tb):
        remove_prefab_importhook()
