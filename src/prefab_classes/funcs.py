from .constants import FIELDS_ATTRIBUTE
from .exceptions import PrefabTypeError


def is_prefab(o):
    cls = o if isinstance(o, type) else type(o)
    return hasattr(cls, FIELDS_ATTRIBUTE)


def is_prefab_instance(o):
    return hasattr(type(o), FIELDS_ATTRIBUTE)


def as_dict(inst, *, excludes=None):
    """
    Represent the prefab as a dictionary of attribute names and values.

    :param inst: Intance of prefab class
    :param excludes: list or set of values to exclude from the resulting dict
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


def to_json(inst, *, excludes=None, default=None, **kwargs):
    """
    Output the class attributes as JSON
    :param inst: Instance of prefab class
    :param excludes: list or set of attributes to exclude from json dump
    :param default: default function for JSON Encoder
    :return:
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
