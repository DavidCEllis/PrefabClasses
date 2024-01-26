from .dynamic import prefab, attribute, build_prefab
from .sentinels import KW_ONLY
from .hook import prefab_compiler
from .funcs import is_prefab, is_prefab_instance

__version__: str
PREFAB_MAGIC_BYTES: bytes

__all__: list[str] = [
    "__version__",
    "prefab",
    "attribute",
    "build_prefab",
    "KW_ONLY",
    "prefab_compiler",
    "is_prefab",
    "is_prefab_instance",
]
