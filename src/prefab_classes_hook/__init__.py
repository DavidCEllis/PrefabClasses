__version__ = "v0.9.1"
PREFAB_MAGIC_BYTES = b"PREFAB_CLASSES_v0.9.1"

from .import_hook import prefab_compiler, insert_prefab_importhook, remove_prefab_importhook
