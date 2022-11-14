import sys

from importlib.machinery import PathFinder

from prefab_classes import prefab_compiler
from prefab_classes.compiled.import_hook import PrefabFinder


def test_hook_present():
    # Test that the contextmanager inserts and removes the PrefabFinder frorm sys.meta_path
    assert PrefabFinder not in sys.meta_path

    with prefab_compiler():
        assert PrefabFinder in sys.meta_path

    assert PrefabFinder not in sys.meta_path


def test_hook_before_pathfinder():
    with prefab_compiler():
        # Check the PrefabFinder has been placed immediately beforer the PathFinder
        assert sys.meta_path.index(PrefabFinder) == sys.meta_path.index(PathFinder) - 1

    # Confirm we don't remove the PathFinder
    assert PathFinder in sys.meta_path
