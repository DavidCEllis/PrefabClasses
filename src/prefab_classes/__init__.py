__version__ = "v0.6.0-alpha"
PREFAB_MAGIC_BYTES = b"_".join([b"PREFAB_CLASSES", __version__.encode()])

from .live import prefab, attribute
from .compiled import prefab_compiler
from .exceptions import PrefabError
