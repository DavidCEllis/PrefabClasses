from .dynamic import prefab, attribute, build_prefab
from .shared import KW_ONLY
from .funcs import is_prefab, is_prefab_instance

__version__: str
PREFAB_MAGIC_BYTES: bytes

__all__: list[str] = [
    "__version__",
    "prefab",
    "attribute",
    "build_prefab",
    "KW_ONLY",
    "is_prefab",
    "is_prefab_instance",
]
