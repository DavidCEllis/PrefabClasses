__version__ = "v0.9.0"
PREFAB_MAGIC_BYTES = b"_".join([b"PREFAB_CLASSES", __version__.encode()])

from .import_hook import prefab_compiler, insert_prefab_importhook, remove_prefab_importhook
