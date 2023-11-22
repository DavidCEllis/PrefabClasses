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
    "prefab_compiler",
    "is_prefab",
    "is_prefab_instance",
]

__version__ = "v0.10.0"
PREFAB_MAGIC_BYTES = b"PREFAB_CLASSES_v0.10.0"

_imports = [
    MultiFromImport(".dynamic", ["prefab", "attribute", "build_prefab"]),
    FromImport(".sentinels", "KW_ONLY"),
    FromImport(".hook", "prefab_compiler"),
    MultiFromImport(".funcs", ["is_prefab", "is_prefab_instance"]),
]

_laz = LazyImporter(_imports, globs=globals())

__getattr__, __dir__ = get_module_funcs(_laz, __name__)
