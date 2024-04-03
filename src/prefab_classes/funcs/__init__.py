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

from .._shared import FIELDS_ATTRIBUTE

from ducktools.lazyimporter import LazyImporter, MultiFromImport

# Importing from collections.abc brings in collections and is slow.
# The actual module is _collections_abc so just import that directly.
# As this module is already imported in python's start this is 'free'
# Backup with the 'official' module in case they change things.
try:
    from _collections_abc import Callable
except ImportError:
    from collections.abc import Callable


__all__ = [
    "is_prefab",
    "is_prefab_instance",
    "as_dict",
    "to_json",
]


_laz = LazyImporter(
    [
        MultiFromImport(
            "._cache_funcs",
            [
                "as_dict_cache",
                "as_dict_json_wrapper",
                "get_json_encoder",
                "merge_defaults",
            ],
        )
    ],
    globs=globals(),
)


def is_prefab(o):
    """
    Identifier function, return True if an object is a prefab class *or* if
    it is an instance of a prefab class.

    The check works by looking for a PREFAB_FIELDS attribute.

    :param o: object for comparison
    :return: True/False
    """
    cls = o if isinstance(o, type) else type(o)
    return hasattr(cls, FIELDS_ATTRIBUTE)


def is_prefab_instance(o):
    """
    Identifier function, return True if an object is an instance of a prefab
    class.

    The check works by looking for a PREFAB_FIELDS attribute.

    :param o: object for comparison
    :return: True/False
    """
    return hasattr(type(o), FIELDS_ATTRIBUTE)


def as_dict(inst, *, excludes: None | tuple[str, ...] = None) -> dict[str, object]:
    """
    Represent the prefab as a dictionary of attribute names stuband values.
    Exclude any keys listed in `excludes`

    This **does not** recurse.

    :param inst: instance of prefab class
    :param excludes: tuple of field names to exclude from the resulting dict
    :return: dictionary {attribute_name: attribute_value, ...}
    """
    return _laz.as_dict_cache(inst.__class__, excludes)(inst)


def to_json(
    inst,
    *,
    excludes: None | tuple[str, ...] = None,
    dumps_func: None | Callable[..., str] = None,  # noqa: false pycharm error
    **kwargs,
) -> str:
    """
    Output the instance attributes as JSON.

    If no dumps function is given and no kwargs are used a basic
    encoder will be reused.

    :param inst: instance of prefab class
    :param excludes: tuple of attribute names to exclude from json
                     caching used internally requires this to be a tuple
                     and not a list
                     **note that these attribute names will be excluded
                     from all prefabs encountered during serialization**
    :param dumps_func: function equivalent to stdlib's json.dumps
                       making it easier to use third party json libraries
    :param kwargs: keyword arguments passed directly to dumps_func
    :return: string of JSON data from the class attributes
    """
    if dumps_func is None and not kwargs:
        encoder = _laz.get_json_encoder(excludes)
        return encoder.encode(inst)
    else:
        default = kwargs.pop("default", None)

        if dumps_func is None:
            import json

            dumps_func = json.dumps

        dict_converter = _laz.as_dict_json_wrapper(excludes)

        if default is None:
            return dumps_func(inst, default=dict_converter, **kwargs)
        else:
            default_func = _laz.merge_defaults(dict_converter, default)
            return dumps_func(inst, default=default_func, **kwargs)
