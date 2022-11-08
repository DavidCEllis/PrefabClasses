from .live.prefab import prefab_register


# noinspection PyProtectedMember
def as_dict(inst, *, init_attributes_only=False):
    """
    Represent the prefab as a dictionary of attribute names and values.

    :param inst: Intance of prefab class
    :param init_attributes_only: Only include attributes that are included in init.
    :return: dictionary {attribute_name: attribute_value, ...}
    """
    result = {}

    if init_attributes_only:
        attrib_names = (name for name, attrib in inst._attributes.items() if attrib.init)
    else:
        attrib_names = inst._attributes.keys()

    for name in attrib_names:
        value = getattr(inst, name)
        result[name] = value
    return result


def to_json(inst, *, excludes=None, indent=2, default=None, **kwargs):
    """
    Output the class attributes as JSON
    :param inst: Instance of prefab class
    :param excludes: list of attributes to exclude from json dump
    :param indent: indent for json
    :param default: default function for JSON Encoder
    :return:
    """
    if excludes:
        out_dict = {
            key: value
            for key, value in as_dict(inst).items()
            if key not in excludes
        }
    else:
        out_dict = as_dict(inst)

    # This function tells the JSON encoder how to serialise Prefab derived objects
    # If the user needs to serialize other classes their default will be called
    # only if the object is not an instance of Prefab
    def default_func(o):
        if o.__class__.__qualname__ in prefab_register:
            return as_dict(o)
        elif default is not None:
            return default(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON Serializable")

    import json  # Only import JSON if needed
    return json.dumps(out_dict, indent=indent, default=default_func, **kwargs)
