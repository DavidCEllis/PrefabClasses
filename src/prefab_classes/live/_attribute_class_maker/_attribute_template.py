# COMPILE_PREFABS
# !THIS IMPORT MUST STAY AT THE TOP!
from prefab_classes import prefab, attribute

# noinspection PyUnresolvedReferences
from ..sentinels import NOTHING

# noinspection PyUnresolvedReferences
from ..exceptions import LivePrefabError


@prefab(compile_prefab=True, compile_slots=True)
class Attribute:
    # Note that the interpreted form of prefab would fail here
    # as it would interpret _NOTHING as no value provided
    # compiled prefabs do not interpret this way.
    default = attribute(default=NOTHING)
    default_factory = attribute(default=NOTHING)
    converter = attribute(default=None)
    init: bool = attribute(default=True)
    repr: bool = attribute(default=True)
    kw_only: bool = attribute(default=False)

    def __prefab_post_init__(self):
        if (
            not self.init
            and self.default is NOTHING
            and self.default_factory is NOTHING
        ):
            raise LivePrefabError(
                "Must provide a default value/factory "
                "if the attribute is not in init."
            )

        if self.kw_only and not self.init:
            raise LivePrefabError(
                "Attribute cannot be keyword only if it is not in init."
            )

        if self.default is not NOTHING and self.default_factory is not NOTHING:
            raise LivePrefabError(
                "Cannot define both a default value and a default factory."
            )
