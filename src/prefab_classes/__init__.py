__version__ = "v0.5.0b"
PREFAB_MAGIC_BYTES = b"_".join([b"PREFAB_CLASSES", __version__.encode()])

from .live import prefab, attribute
from .compiled import prefab_compiler
from .exceptions import PrefabError
