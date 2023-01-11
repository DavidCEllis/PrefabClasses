from functools import lru_cache, partial

from .constants import FIELDS_ATTRIBUTE

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
        raise TypeError(f"inst should be a prefab instance, not {cls}")

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
    return _as_dict_cache(type(inst), excludes)(inst)


def _as_dict_json_wrapper(inst, *, excludes: "Optional[tuple[str, ...]]" = None):
    """Wrapper that gives a more accurate TypeError message for serialization"""
    try:
        return _as_dict_cache(type(inst), excludes)(inst)
    except TypeError:
        raise TypeError(f"Object of type {type(inst).__name__} is not JSON serializable")


@lru_cache
def _get_json_encoder(excludes: "Optional[tuple[str, ...]]" = None):
    import json
    return json.JSONEncoder(default=partial(_as_dict_json_wrapper, excludes=excludes))


@lru_cache
def _merge_defaults(*defaults):
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
            raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
    return default


def to_json(
        inst,
        *,
        excludes: "Optional[tuple[str, ...]]" = None,
        dumps_func: "Callable" = None,
        **kwargs
) -> str:
    """
    Output the class attributes as JSON

    If no dumps function it will attempt to reuse the basic encoder

    :param inst: instance of prefab class
    :param excludes: tuple of attribute names to exclude from json
                     **note that these attribute names will be excluded
                     from all prefabs encountered during serialization**
    :param dumps_func: function equivalent to stdlib's json.dumps
                       making it easier to use third party json libraries.
    :param kwargs: keyword arguments passed directly to dumps_func
    :return: String of JSON data from the class attributes
    """
    if dumps_func is None and not kwargs:
        encoder = _get_json_encoder(excludes)
        return encoder.encode(inst)
    else:
        default = kwargs.pop('default', None)

        if dumps_func is None:
            import json
            dumps_func = json.dumps

        as_dict_excludes = partial(as_dict, excludes=excludes)

        if default is None:
            return dumps_func(inst, default=as_dict_excludes, **kwargs)
        else:
            default_func = _merge_defaults(as_dict_excludes, default)
            return dumps_func(inst, default=default_func, **kwargs)
