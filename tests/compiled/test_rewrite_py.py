from prefab_classes.compiled import rewrite_to_py
from pathlib import Path

# Don't include the version number for this test.
COMPILE_COMMENT = """
# DO NOT MANUALLY EDIT THIS FILE
# MODULE: {dest}
# GENERATED FROM: {source}
""".strip()


def test_rewrite_to_py():
    base = Path(__file__).parent / "compile_targets"

    source_file = base / "example_to_compile.py"
    expected_file = base / "example_to_compile_expected.py"
    temporary_output = base / "example_to_compile_expected_temp.py"

    expected_output = expected_file.read_text(encoding="utf-8")

    rewrite_to_py(
        source_file,
        temporary_output,
        header_comment=COMPILE_COMMENT,
    )

    true_output = temporary_output.read_text(encoding="utf-8")

    temporary_output.unlink()

    assert expected_output == true_output
