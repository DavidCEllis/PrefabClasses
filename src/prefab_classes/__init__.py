__version__ = "v0.7.7"
PREFAB_MAGIC_BYTES = b"_".join([b"PREFAB_CLASSES", __version__.encode()])

from .dynamic import prefab, attribute
from .sentinels import KW_ONLY
