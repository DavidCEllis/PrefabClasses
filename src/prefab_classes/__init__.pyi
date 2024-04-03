from ._class_generator import prefab, attribute, build_prefab, SlotAttributes
from ._shared import KW_ONLY, PrefabError
from .funcs import is_prefab, is_prefab_instance

__version__: str

__all__: list[str] = [
    "__version__",
    "prefab",
    "attribute",
    "build_prefab",
    "SlotAttributes",
    "KW_ONLY",
    "PrefabError",
    "is_prefab",
    "is_prefab_instance",
]
