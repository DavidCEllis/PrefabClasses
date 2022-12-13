"""Sentinel values that get used in multiple files"""

__all__ = ["NOTHING", "KW_ONLY"]

# Special indicator to use in places where NONE could be a legitimate value
# to indicate that no value has been set.
class _NOTHING_TYPE:
    def __repr__(self):
        return "<NOTHING Sentinel Object>"


NOTHING = _NOTHING_TYPE()


# KW_ONLY sentinel 'type' to use to indicate all subsequent attributes are
# keyword only
class _KW_ONLY_TYPE:
    def __repr__(self):
        return "<KW_ONLY Sentinel Object>"


KW_ONLY = _KW_ONLY_TYPE
