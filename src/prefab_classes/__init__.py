# ==============================================================================
# Copyright (c) 2022-2024 David C Ellis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

from ducktools.lazyimporter import (
    LazyImporter,
    MultiFromImport,
    get_module_funcs,
)

# noinspection PyUnresolvedReferences
__all__ = [
    "__version__",
    "prefab",
    "attribute",
    "build_prefab",
    "SlotAttributes" "KW_ONLY",
    "PrefabError",
    "is_prefab",
    "is_prefab_instance",
]

__version__ = "v0.12.0"

_imports = [
    MultiFromImport(
        "._class_generator", ["prefab", "attribute", "build_prefab", "SlotAttributes"]
    ),
    MultiFromImport("._shared", ["KW_ONLY", "PrefabError"]),
    MultiFromImport(".funcs", ["is_prefab", "is_prefab_instance"]),
]

_laz = LazyImporter(_imports, globs=globals())

__getattr__, __dir__ = get_module_funcs(_laz, __name__)
