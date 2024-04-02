from ducktools.lazyimporter import (
    LazyImporter,
    MultiFromImport,
    get_module_funcs,
)

# noinspection PyUnresolvedReferences
__all__ = [
    "__version__",
    "prefab",
    "attribute",
    "build_prefab",
    "KW_ONLY",
    "PrefabError",
    "is_prefab",
    "is_prefab_instance",
]

__version__ = "v0.12.0"

_imports = [
    MultiFromImport("._class_generator", ["prefab", "attribute", "build_prefab"]),
    MultiFromImport("._shared", ["KW_ONLY", "PrefabError"]),
    MultiFromImport(".funcs", ["is_prefab", "is_prefab_instance"]),
]

_laz = LazyImporter(_imports, globs=globals())

__getattr__, __dir__ = get_module_funcs(_laz, __name__)
