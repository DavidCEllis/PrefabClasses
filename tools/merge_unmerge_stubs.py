# For testing the stubs it is useful to merge them into the src/ tree, however while they are incomplete
# I would like to keep them separate.

from pathlib import Path
import os

stubs_base = Path(__file__).parents[1] / "stubs"
src_base = Path(__file__).parents[1] / "src"

stub_files = list(stubs_base.glob("**/*.pyi"))
stubs_in_src = list(src_base.glob("**/*.pyi"))

typed_files = [
    src_base / "prefab_classes" / "py.typed",
    src_base / "prefab_classes_hook" / "py.typed"
]

def merge_stubs():
    print("Merging stubs into src folder")
    for item in stub_files:
        src = str(item)
        dest = str(src_base / item.relative_to(stubs_base))
        os.rename(src, dest)

    for item in typed_files:
        item.touch()

def unmerge_stubs():
    print("Removing stubs from src folder")
    for item in stubs_in_src:
        src = str(item)
        dest = str(stubs_base / item.relative_to(src_base))
        os.rename(src, dest)

    for item in typed_files:
        item.unlink()


if stubs_in_src:
    unmerge_stubs()
elif stub_files:
    merge_stubs()
else:
    print("No Stubs Present")
