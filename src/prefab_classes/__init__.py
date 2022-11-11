__version__ = "v0.5.0b"
from .live import prefab, attribute
from .compiled import insert_prefab_importhook, remove_prefab_importhook
from .exceptions import PrefabError
