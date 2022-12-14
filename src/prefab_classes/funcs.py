from collections.abc import Container
from typing import Optional

from .constants import FIELDS_ATTRIBUTE
from .exceptions import PrefabTypeError


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


def as_dict(inst, *, excludes: Optional[Container[str]] = None):
    """
    Represent the prefab as a dictionary of attribute names and values.
    Exclude any keys listed in `excludes`

    This **does not** recurse.

    :param inst: instance of prefab class
    :param excludes: container of values to exclude from the resulting dict
    :return: dictionary {attribute_name: attribute_value, ...}
    """
    if not is_prefab_instance(inst):
        raise PrefabTypeError(f"inst hould be a prefab instance, not {type(inst)}")
    result = {}
    excludes = excludes or set()

    attrib_names = getattr(inst, FIELDS_ATTRIBUTE)

    for name in attrib_names:
        if name not in excludes:
            value = getattr(inst, name)
            result[name] = value
    return result


def to_json(
        inst,
        *,
        excludes: Optional[Container[str]] = None,
        default=None,
        **kwargs
) -> str:
    """
    Output the class attributes as JSON

    This will recurse through as json.dumps does. A default function
    can be provided as an argument as it can for json.dumps.

    :param inst: instance of prefab class
    :param excludes: container of attributes to exclude from json dump
    :param default: default function for JSON Encoder
    :return: String of JSON data from the class attributes
    """

    out_dict = as_dict(inst, excludes=excludes)

    # This function tells the JSON encoder how to serialise Prefab derived objects
    # If the user needs to serialize other classes their default will be called
    # only if the object is not an instance of Prefab
    def default_func(o):
        if is_prefab(o):
            return as_dict(o)
        elif default is not None:
            return default(o)
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON Serializable"
        )

    import json  # Only import JSON if needed

    return json.dumps(out_dict, default=default_func, **kwargs)
