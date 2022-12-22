# ==============================================================================
# Copyright (c) 2022 David C Ellis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
Handle boilerplate generation for classes.
"""
import sys
import warnings

# Import speed optimization
# The C implementation can import nearly 100x faster
# and will usually be available.
try:
    from _functools import partial
except ImportError:
    from functools import partial

# Inspect is a slow import, it's only used for pre/post init
# functions, if those aren't used there's no need for it
# So now it's imported only when analyzing those functions
# import inspect

# Typing is also a slow import, so we use the dataclass_transform
# function copied from the module instead
SLOW_TYPING = True
if SLOW_TYPING:
    from .._typing import dataclass_transform
else:
    try:
        # noinspection PyProtectedMember
        from typing import dataclass_transform
    except ImportError:
        from typing_extensions import dataclass_transform

from ._attribute_class import Attribute
from ..constants import (
    FIELDS_ATTRIBUTE,
    COMPILED_FLAG,
    CLASSVAR_NAME,
    PRE_INIT_FUNC,
    POST_INIT_FUNC,
)
from ..exceptions import PrefabError, LivePrefabError, CompiledPrefabError
from ..sentinels import NOTHING, KW_ONLY
from .method_generators import (
    init_maker,
    repr_maker,
    eq_maker,
    iter_maker,
    prefab_init_maker,
)


def _is_classvar(hint):
    _typing = sys.modules.get("typing")
    if _typing:
        if (
            hint is _typing.ClassVar
            or getattr(hint, "__origin__", None) is _typing.ClassVar
        ):
            return True
        # String used as annotation
        elif isinstance(hint, str) and CLASSVAR_NAME in hint:
            return True
    return False


def attribute(
    *,
    default=NOTHING,
    default_factory=NOTHING,
    converter=None,  # DEPRECATED
    init=True,
    repr=True,
    kw_only=False,
    exclude_field=False,
):
    """
    Additional definition for how to generate standard methods
    for an instance attribute.

    **NOTE**: There is currently a `converter` parameter that will be removed in a future version.

    :param default: Default value for this attribute
    :param default_factory: 0 argument callable to give a default value
                            (for otherwise mutable defaults, eg: list)
    :param init: Include this attribute in the __init__ parameters
    :param repr: Include this attribute in the class __repr__
    :param kw_only: Make this argument keyword only in init
    :param exclude_field: Exclude this field from all magic method generation
                          apart from __init__
                          and do not include it in PREFAB_FIELDS

    :return: Attribute generated with these parameters.
    """
    if converter is not None:
        warnings.warn(
            DeprecationWarning(
                "Converters will be removed in v1.0. "
                "This behaviour has been replaced by __prefab_post_init__"
            )
        )
    return Attribute(
        default=default,
        default_factory=default_factory,
        converter=converter,
        init=init,
        repr=repr,
        kw_only=kw_only,
        exclude_field=exclude_field,
    )


def _make_prefab(
    cls: type,
    *,
    init=True,
    repr=True,
    eq=True,
    iter=False,
    match_args=True,
    kw_only=False,
):
    """
    Generate boilerplate code for dunder methods in a class.

    :param cls: Class to convert to a prefab
    :param init: generate __init__
    :param repr: generate __repr__
    :param eq: generate __eq__
    :param iter: generate __iter__
    :param match_args: generate __match_args__
    :param kw_only: Make all attributes keyword only
    :return: class with __ methods defined
    """
    # Here first we need to look at type hints for the type hint
    # syntax variant.
    # If a key exists and is *NOT* in __annotations__ then all
    # annotations will be ignored as it becomes complex to fix the
    # ordering.

    # Make a copy of the __annotations__ dictionary
    cls_annotations = getattr(cls, "__annotations__", {}).copy()

    cls_annotation_names = cls_annotations.keys()

    cls_attributes = {k: v for k, v in vars(cls).items() if isinstance(v, Attribute)}

    cls_attribute_names = cls_attributes.keys()

    if set(cls_annotation_names).issuperset(set(cls_attribute_names)):
        # replace the classes' attributes dict with one with the correct
        # order from the annotations.
        kw_flag = False
        new_attributes = {}
        for name, value in cls_annotations.items():
            # Ignore ClassVar hints
            if _is_classvar(value):
                continue

            # Look for the KW_ONLY annotation
            if value is KW_ONLY or value == "KW_ONLY":
                if kw_flag:
                    raise LivePrefabError(
                        "Class can not be defined as keyword only twice"
                    )
                kw_flag = True
            else:
                # Copy atributes that are already defined to the new dict
                # generate Attribute() values for those that are not defined.
                if hasattr(cls, name):
                    if name in cls_attribute_names:
                        attrib = cls_attributes[name]
                    else:
                        attribute_default = getattr(cls, name)
                        attrib = attribute(default=attribute_default)

                    # Clear the attribute from the class after it has been used
                    # in the definition.
                    delattr(cls, name)
                else:
                    attrib = attribute()

                if kw_flag or kw_only:
                    attrib.kw_only = True

                attrib._type = cls_annotations[name]
                new_attributes[name] = attrib

            # Remove the original annotation
            del cls.__annotations__[name]
        cls_attributes = new_attributes
    else:
        for name, attrib in cls_attributes.items():
            if kw_only:
                attrib.kw_only = True

            delattr(cls, name)
            # Some items can still be annotated.
            try:
                attrib._type = cls.__annotations__[name]
                del cls.__annotations__[name]
            except (AttributeError, KeyError):
                # AttributeError as 3.9 does not guarantee the existence of __annotations__
                pass

    setattr(cls, f"_{cls.__name__}_attributes", cls_attributes)

    mro = cls.__mro__[:-1]  # skip 'object' base class

    # Handle inheritance
    if mro == (cls,):  # special case of no inheritance.
        attributes = cls_attributes.copy()
    else:
        attributes = {}
        for c in reversed(mro):
            try:
                attributes.update(getattr(c, f"_{c.__name__}_attributes"))
            except AttributeError:
                pass

    # Check pre_init and post_init functions if they exist
    try:
        func = getattr(cls, PRE_INIT_FUNC)
    except AttributeError:
        pass
    else:
        import inspect
        signature = inspect.signature(func)
        for item in signature.parameters.keys():
            if item not in attributes.keys() and item != "self":
                raise LivePrefabError(
                    f"{item} argument in __prefab_pre_init__ is not a valid attribute."
                )

    post_init_args = []
    try:
        func = getattr(cls, POST_INIT_FUNC)
    except AttributeError:
        pass
    else:
        import inspect
        signature = inspect.signature(func)
        for item in signature.parameters.keys():
            if item != "self":
                if item not in attributes.keys():
                    raise LivePrefabError(
                        f"{item} argument in __prefab_post_init__ is not a valid attribute."
                    )
                post_init_args.append(item)

    default_defined = []
    valid_fields = []
    for name, attrib in attributes.items():
        if attrib.exclude_field:
            if name not in post_init_args:
                raise LivePrefabError(
                    f"{name} is an excluded attribute but is not passed to post_init"
                )
        else:
            valid_fields.append(name)

        if attrib.init and not attrib.kw_only:
            if attrib.default is not NOTHING or attrib.default_factory is not NOTHING:
                default_defined.append(name)
            else:
                if default_defined:
                    names = ", ".join(default_defined)
                    raise SyntaxError(
                        "non-default argument follows default argument",
                        f"defaults: {names}",
                        f"non_default after default: {name}",
                    )

    setattr(cls, FIELDS_ATTRIBUTE, valid_fields)
    cls._attributes = attributes
    if match_args and "__match_args__" not in cls.__dict__:
        cls.__match_args__ = tuple(valid_fields)

    if init and "__init__" not in cls.__dict__:
        setattr(cls, "__init__", init_maker)
    else:
        setattr(cls, "__prefab_init__", prefab_init_maker)
    if repr and "__repr__" not in cls.__dict__:
        setattr(cls, "__repr__", repr_maker)
    if eq and "__eq__" not in cls.__dict__:
        setattr(cls, "__eq__", eq_maker)
    if iter and "__iter__" not in cls.__dict__:
        setattr(cls, "__iter__", iter_maker)

    return cls


@dataclass_transform(field_specifiers=(attribute,))
def prefab(
    cls: type = None,
    *,
    init=True,
    repr=True,
    eq=True,
    iter=False,
    match_args=True,
    kw_only=False,
    compile_prefab=False,
    compile_fallback=False,
    compile_plain=False,
    compile_slots=False,
):
    """
    Generate boilerplate code for dunder methods in a class.

    Use as a decorator.

    :param cls: Class to convert to a prefab
    :param init: generates __init__ if true or __prefab_init__ if false
    :param repr: generate __repr__
    :param eq: generate __eq__
    :param iter: generate __iter__
    :param match_args: generate __match_args__
    :param kw_only: make all attributes keyword only

    :param compile_prefab: Direct the prefab compiler to compile this class
    :param compile_fallback: Fallback to a dynamic prefab if not compiled.
    :param compile_plain: Do not include the COMPILED and PREFAB_FIELDS
                          attributes after compilation
    :param compile_slots: Make the resulting compiled class use slots
    :return: class with __ methods defined
    """
    if not cls:
        # Called as () method to change defaults
        # Skip compile arguments other than prefab/fallback
        # These are not needed
        return partial(
            prefab,
            init=init,
            repr=repr,
            eq=eq,
            iter=iter,
            match_args=match_args,
            compile_prefab=compile_prefab,
            compile_fallback=compile_fallback,
            kw_only=kw_only,
        )
    else:
        if getattr(cls, COMPILED_FLAG, False):
            # Do not recompile compiled classes
            return cls
        # If the class is not compiled but has the instruction to compile, fail
        elif compile_prefab and not compile_fallback:
            raise CompiledPrefabError(
                f"Class {cls.__name__} has not been compiled and compiled_fallback=False.",
                f"Make sure the comment '# COMPILE_PREFABS' is at the "
                f"top of the module {cls.__module__}\n"
                f"and the module is imported in a 'with prefab_compiler():' block",
            )
        elif compile_slots:
            raise PrefabError("Slots are not supported on 'dynamic' Prefabs.")
        else:
            # Create Live Version
            setattr(cls, COMPILED_FLAG, False)
            return _make_prefab(
                cls,
                init=init,
                repr=repr,
                eq=eq,
                iter=iter,
                match_args=match_args,
                kw_only=kw_only,
            )
