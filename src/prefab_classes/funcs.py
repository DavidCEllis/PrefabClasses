from .constants import FIELDS_ATTRIBUTE


def is_prefab(o):
    return hasattr(o, FIELDS_ATTRIBUTE)
