from ducktools.lazyimporter import (
    LazyImporter,
    MultiFromImport,
    FromImport,
    get_module_funcs,
)

# noinspection PyUnresolvedReferences
__all__ = [
    "__version__",
    "prefab",
    "attribute",
    "build_prefab",
    "KW_ONLY",
    "is_prefab",
    "is_prefab_instance",
]

__version__ = "v0.11.1"
PREFAB_MAGIC_BYTES = b"PREFAB_CLASSES_v0.11.1"

_imports = [
    MultiFromImport(".dynamic", ["prefab", "attribute", "build_prefab"]),
    FromImport(".shared", "KW_ONLY"),
    MultiFromImport(".funcs", ["is_prefab", "is_prefab_instance"]),
]

_laz = LazyImporter(_imports, globs=globals())

__getattr__, __dir__ = get_module_funcs(_laz, __name__)
