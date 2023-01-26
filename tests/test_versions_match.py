from prefab_classes import __version__ as base_version, PREFAB_MAGIC_BYTES as BASE_BYTES
from prefab_classes_hook import __version__ as hook_version, PREFAB_MAGIC_BYTES as HOOK_BYTES

def test_versions_in_sync():
    assert base_version == hook_version
    assert BASE_BYTES == HOOK_BYTES
