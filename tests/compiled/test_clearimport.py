"""
Test that prefab_classes imports are removed correctly after importing the module.
Check they are only removed if they are not otherwise used.
"""

import pytest

from prefab_classes.hook import prefab_compiler

clear_module_names = [
    ("example_import_clear", "W"),
    ("example_import_clear2", "X"),
    ("example_import_clear3", "Y"),
    ("example_import_clear4", "Z"),
]

# noinspection PyUnresolvedReferences
@pytest.mark.parametrize(["module_name", "class_letter"], clear_module_names)
@pytest.mark.usefixtures("compile_folder_modules")
def test_cleared_prefab(module_name, class_letter):
    with prefab_compiler():
        example_import_clear = __import__(
            module_name, globals=globals(), locals=locals()
        )

    assert getattr(example_import_clear, class_letter).COMPILED

    assert "collections" in example_import_clear.__dict__
    assert "functools" in example_import_clear.__dict__
    assert "prefab" not in example_import_clear.__dict__
    assert "attribute" not in example_import_clear.__dict__


@pytest.mark.parametrize(
    "module_name", ["example_import_noclear_dynamic", "example_import_noclear_dynamic2"]
)
@pytest.mark.usefixtures("compile_folder_modules")
def test_uncleared_prefab_dynamic(module_name):
    with prefab_compiler():
        example_import_noclear = __import__(
            module_name, globals=globals(), locals=locals()
        )

    assert example_import_noclear.X.COMPILED
    assert not example_import_noclear.Y.COMPILED

    assert "collections" in example_import_noclear.__dict__
    assert "functools" in example_import_noclear.__dict__
    assert "prefab" in example_import_noclear.__dict__
    assert "attribute" in example_import_noclear.__dict__


@pytest.mark.usefixtures("compile_folder_modules")
def test_uncleared_prefab_makeprefab():
    with prefab_compiler():
        example_import_noclear = __import__(
            "example_import_noclear_makeprefab", globals=globals(), locals=locals()
        )

    assert example_import_noclear.X.COMPILED
    assert not example_import_noclear.Y.COMPILED

    assert "collections" in example_import_noclear.__dict__
    assert "functools" in example_import_noclear.__dict__
    assert "prefab" in example_import_noclear.__dict__
    assert "attribute" in example_import_noclear.__dict__
