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

__all__ = [
    "PRE_INIT_FUNC",
    "POST_INIT_FUNC",
    "PREFAB_INIT_FUNC",
    "DECORATOR_NAME",
    "ATTRIBUTE_FUNCNAME",
    "FIELDS_ATTRIBUTE",
    "CLASSVAR_NAME",
    "INTERNAL_DICT",
    "PrefabError",
    "NOTHING",
    "KW_ONLY",
]


# CONSTANT STRINGS
# DO NOT CHANGE - EXTERNALLY USABLE NAMES
PRE_INIT_FUNC = "__prefab_pre_init__"
POST_INIT_FUNC = "__prefab_post_init__"
PREFAB_INIT_FUNC = "__prefab_init__"
DECORATOR_NAME = "prefab"
ATTRIBUTE_FUNCNAME = "attribute"

# WILL PROBABLY BREAK CODE
FIELDS_ATTRIBUTE = "PREFAB_FIELDS"
CLASSVAR_NAME = "ClassVar"
INTERNAL_DICT = "__prefab_internals__"


# EXCEPTIONS
class PrefabError(Exception):
    pass


# SENTINEL VALUES


# Special indicator to use in places where NONE could be a legitimate value
# to indicate that no value has been set.
# noinspection PyPep8Naming
class _NOTHING_TYPE:
    def __repr__(self):
        return "<NOTHING Sentinel Object>"


NOTHING = _NOTHING_TYPE()


# KW_ONLY sentinel 'type' to use to indicate all subsequent attributes are
# keyword only
# noinspection PyPep8Naming
class _KW_ONLY_TYPE:
    def __repr__(self):
        return "<KW_ONLY Sentinel Object>"


KW_ONLY = _KW_ONLY_TYPE()
