__version__ = "v0.8.2"
PREFAB_MAGIC_BYTES = b"_".join([b"PREFAB_CLASSES", __version__.encode()])

from .dynamic import prefab, attribute, build_prefab
from .sentinels import KW_ONLY
