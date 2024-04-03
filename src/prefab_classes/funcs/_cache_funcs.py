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

from functools import lru_cache

from .._shared import FIELDS_ATTRIBUTE


@lru_cache
def as_dict_cache(cls, excludes=None):
    try:
        attrib_names = getattr(cls, FIELDS_ATTRIBUTE)
    except AttributeError:
        raise TypeError(f"inst should be a prefab instance, not {cls}")

    if excludes:
        vals = ", ".join(
            f"'{item}': obj.{item}" for item in attrib_names if item not in excludes
        )
    else:
        vals = ", ".join(f"'{item}': obj.{item}" for item in attrib_names)
    out_dict = f"{{{vals}}}"
    funcdef = f"def asdict(obj): return {out_dict}"
    globs, locs = {}, {}
    exec(funcdef, globs, locs)
    method = locs["asdict"]
    return method


@lru_cache
def as_dict_json_wrapper(excludes: None | tuple[str, ...] = None):
    def _as_dict_json_inner(inst):
        """Wrapper that gives a more accurate TypeError message for serialization"""
        try:
            return as_dict_cache(type(inst), excludes)(inst)
        except TypeError:
            raise TypeError(
                f"Object of type {type(inst).__name__} is not JSON serializable"
            )

    return _as_dict_json_inner


@lru_cache
def get_json_encoder(excludes: None | tuple[str, ...] = None):
    import json

    return json.JSONEncoder(default=as_dict_json_wrapper(excludes))


@lru_cache
def merge_defaults(*defaults):
    """
    Combine multiple default functions into one.

    Default functions are expected to return serializable objects or raise a TypeError

    :param defaults: 'default' functions for json.dumps
    :return: merged default function
    """

    def default(o):
        for func in defaults:
            try:
                return func(o)
            except TypeError:
                pass
        else:
            raise TypeError(
                f"Object of type {type(o).__name__} is not JSON serializable"
            )

    return default
