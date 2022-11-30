from .default_sentinels import _NOTHING
from ..exceptions import LivePrefabError


class Attribute:
    __slots__ = (
        "default",
        "default_factory",
        "converter",
        "init",
        "repr",
        "kw_only",
    )

    def __init__(
        self,
        *,
        default=_NOTHING,
        default_factory=_NOTHING,
        converter=None,
        init=True,
        repr=True,
        kw_only=False,
    ):
        """
        Initialize an Attribute

        :param default: Default value for this attribute
        :param default_factory: No argument callable to give a default value
                                (for otherwise mutable defaults)
        :param converter: prefab.attr = x -> prefab.attr = converter(x)
        :param init: Include this attribute in the __init__ parameters
        :param repr: Include this attribute in the class __repr__
        :param kw_only: Make this argument keyword only in init
        """

        if not init and default is _NOTHING and default_factory is _NOTHING:
            raise LivePrefabError(
                "Must provide a default value/factory "
                "if the attribute is not in init."
            )

        if kw_only and not init:
            raise LivePrefabError(
                "Attribute cannot be keyword only if it is not in init."
            )

        if default is not _NOTHING and default_factory is not _NOTHING:
            raise LivePrefabError(
                "Cannot define both a default value and a default factory."
            )

        self.default = default
        self.default_factory = default_factory
        self.converter = converter
        self.init = init
        self.repr = repr
        self.kw_only = kw_only

    def __repr__(self):
        return (
            f"Attribute("
            f"default={self.default!r}, "
            f"default_factory={self.default_factory!r}, "
            f"converter={self.converter!r}, "
            f"init={self.init!r}, "
            f"repr={self.repr!r}, "
            f"kw_only={self.kw_only!r}"
            f")"
        )
