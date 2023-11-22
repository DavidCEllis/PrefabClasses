import sys
from importlib.machinery import PathFinder
from unittest import mock

import pytest

from prefab_classes.hook import prefab_compiler, PrefabFinder, PrefabHacker


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


@pytest.mark.usefixtures("compile_folder_modules")
def test_invalidation_from_compiled():
    # Test the python importer will invalidate Prefab compiled .pyc files
    with prefab_compiler():
        import example_fallback

    # Check this is not a 'dynamic' prefab
    assert example_fallback.Coordinate.COMPILED is True

    # remove the module
    del sys.modules["example_fallback"]

    import example_fallback

    # Show this is now a 'dynamic' prefab
    assert example_fallback.Coordinate.COMPILED is False


@pytest.mark.usefixtures("compile_folder_modules")
def test_invalidation_to_compiled():
    # Test the prefab importer will invalidate standard python compiled pyc files
    import example_fallback

    # Check this is not a 'dynamic' prefab
    assert example_fallback.Coordinate.COMPILED is False

    # remove the module
    del sys.modules["example_fallback"]

    with prefab_compiler():
        import example_fallback

    # Show this is now a 'dynamic' prefab
    assert example_fallback.Coordinate.COMPILED is True


@pytest.mark.usefixtures("compile_folder_modules")
def test_cache_used():
    # Test that if a .pyc compiled version of a prefab class exists that
    # it will be used and not recompiled
    stc_call_checker = mock.MagicMock()  # source_to_code
    gc_call_checker = mock.MagicMock()  # get_code

    def mock_wrapper(method, mock_obj):
        def wrapped(*args, **kwargs):
            mock_obj(*args, **kwargs)
            return method(*args, **kwargs)

        return wrapped

    mock_stc = mock_wrapper(PrefabHacker.source_to_code, stc_call_checker)
    mock_gc = mock_wrapper(PrefabHacker.get_code, gc_call_checker)

    with (
        mock.patch.object(PrefabHacker, "source_to_code", mock_stc),
        mock.patch.object(PrefabHacker, "get_code", mock_gc),
    ):
        with prefab_compiler():
            import example_fallback

    # Confirm the code has been compiled as source_to_code and get_code have been used
    stc_call_checker.assert_called_once()
    gc_call_checker.asser_called_once()

    stc_call_checker.reset_mock()
    gc_call_checker.reset_mock()

    assert example_fallback.Coordinate.COMPILED  # Check the code is actually there

    # Clear modules to allow second import
    del sys.modules["example_fallback"]

    # Patch the importer to test if a method is not called.
    with (
        mock.patch.object(PrefabHacker, "source_to_code", mock_stc),
        mock.patch.object(PrefabHacker, "get_code", mock_gc),
    ):
        with prefab_compiler():
            import example_fallback

    # Check source_to_code not called the second time but get_code still called.
    stc_call_checker.assert_not_called()
    gc_call_checker.assert_called()

    assert example_fallback.Coordinate.COMPILED
