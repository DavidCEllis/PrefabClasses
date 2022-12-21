from collections.abc import Container
from functools import lru_cache, partial

from .constants import FIELDS_ATTRIBUTE
from .exceptions import PrefabTypeError

# noinspection PyUnreachableCode
if False:
    from typing import Optional, Callable


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


@lru_cache
def _as_dict_cache(cls, excludes=None):
    try:
        attrib_names = getattr(cls, FIELDS_ATTRIBUTE)
    except AttributeError:
        raise PrefabTypeError(f"inst should be a prefab instance, not {cls}")

    if excludes:
        vals = ", ".join(f"'{item}': obj.{item}" for item in attrib_names if item not in excludes)
    else:
        vals = ", ".join(f"'{item}': obj.{item}" for item in attrib_names)
    out_dict = f"{{{vals}}}"
    funcdef = f"def asdict(obj): return {out_dict}"
    globs, locs = {}, {}
    exec(funcdef, globs, locs)
    method = locs['asdict']
    return method


def as_dict(inst, *, excludes: "Optional[tuple[str, ...]]" = None):
    """
    Represent the prefab as a dictionary of attribute names and values.
    Exclude any keys listed in `excludes`

    This **does not** recurse.

    :param inst: instance of prefab class
    :param excludes: tuple of field names to exclude from the resulting dict
    :return: dictionary {attribute_name: attribute_value, ...}
    """
    return _as_dict_cache(inst.__class__, excludes)(inst)


def as_dict_uncached(inst, *, excludes: "Optional[Container[str]]" = None):
    """
    Represent the prefab as a dictionary of attribute names and values.
    Exclude any keys listed in `excludes`

    This **does not** recurse.

    :param inst: instance of prefab class
    :param excludes: collection of values to exclude from the resulting dict
    :return: dictionary {attribute_name: attribute_value, ...}
    """
    try:
        attrib_names = getattr(inst, FIELDS_ATTRIBUTE)
    except AttributeError:
        raise PrefabTypeError(f"inst should be a prefab instance, not {type(inst)}")

    if not excludes:
        result = {name: getattr(inst, name) for name in attrib_names}
    else:
        excludes = excludes or set()
        result = {name: getattr(inst, name) for name in attrib_names if name not in excludes}
    return result


def to_json(
        inst,
        *,
        excludes: "Optional[tuple[str, ...]]" = None,
        dumps_func: "Callable" = None,
        **kwargs
) -> str:
    """
    Output the class attributes as JSON

    This is essentially a wrapper around any `dumps` function provided.
    The main advantage is it will let you pass an additional 'default'
    function into the default argument and it makes it easier to use
    excludes.

    :param inst: instance of prefab class
    :param excludes: tuple of attribute names to exclude from json
                     **note that these attribute names will be excluded
                     from all prefabs encountered during serialization**
    :param dumps_func: function equivalent to stdlib's json.dumps
                       making it easier to use third party json libraries.
    :param kwargs: keyword arguments passed directly to dumps_func
    :return: String of JSON data from the class attributes
    """

    as_dict_excludes = partial(as_dict, excludes=excludes)

    default = kwargs.pop('default', None)

    # This function tells the JSON encoder how to serialise Prefab derived objects
    # If the user needs to serialize other classes their default will be called
    # only if the object is not an instance of Prefab
    def default_func(o):
        if is_prefab_instance(o):
            return as_dict_excludes(o)
        elif default is not None:
            return default(o)
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON Serializable"
        )

    if dumps_func is None:
        import json  # Only import JSON if needed
        dumps_func = json.dumps

    return dumps_func(inst, default=default_func, **kwargs)
