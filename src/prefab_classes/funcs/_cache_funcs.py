from functools import lru_cache

from ..constants import FIELDS_ATTRIBUTE


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
