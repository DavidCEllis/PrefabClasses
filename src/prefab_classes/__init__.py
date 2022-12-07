__version__ = "v0.7.1"
PREFAB_MAGIC_BYTES = b"_".join([b"PREFAB_CLASSES", __version__.encode()])

from .live import prefab, attribute
from .compiled import prefab_compiler
from .exceptions import PrefabError
from .funcs import is_prefab, to_json, as_dict
from .sentinels import KW_ONLY
