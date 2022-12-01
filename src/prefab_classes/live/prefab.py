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
from functools import partial

# noinspection PyUnresolvedReferences
# from typing import dataclass_transform

from ._attribute_class import Attribute
from ..constants import FIELDS_ATTRIBUTE, COMPILED_FLAG, CLASSVAR_NAME
from ..exceptions import PrefabError, LivePrefabError, CompiledPrefabError
from .default_sentinels import _NOTHING
from .method_generators import (
    init_maker,
    repr_maker,
    eq_maker,
    iter_maker,
    prefab_init_maker,
)


def attribute(
    *,
    default=_NOTHING,
    default_factory=_NOTHING,
    converter=None,
    init=True,
    repr=True,
    kw_only=False,
):
    """
    Get an Attribute instance
    indirect to allow for potential changes in the future

    :param default: Default value for this attribute
    :param default_factory: No argument callable to give a default value
                            (for otherwise mutable defaults)
    :param converter: prefab.attr = x -> prefab.attr = converter(x)
    :param init: Include this attribute in the __init__ parameters
    :param repr: Include this attribute in the class __repr__
    :param kw_only: Make this argument keyword only in init

    :return: Attribute generated with these parameters.
    """
    return Attribute(
        default=default,
        default_factory=default_factory,
        converter=converter,
        init=init,
        repr=repr,
        kw_only=kw_only,
    )


# @dataclass_transform(field_specifiers=(attribute, Attribute))
def _make_prefab(
    cls: type, *, init=True, repr=True, eq=True, iter=False, match_args=True
):
    """
    Generate boilerplate code for dunder methods in a class.

    :param cls: Class to convert to a prefab
    :param init: generate __init__
    :param repr: generate __repr__
    :param eq: generate __eq__
    :param iter: generate __iter__
    :param match_args: generate __match_args__
    :return: class with __ methods defined
    """
    # Here first we need to look at type hints for the type hint
    # syntax variant.
    # If a key exists and is *NOT* in __annotations__ then all
    # annotations will be ignored as it becomes complex to fix the
    # ordering.

    annotations = getattr(cls, "__annotations__", {})
    # Eliminate ClassVars - don't want to import typing if
    # it's not already imported
    if annotations:
        _typing = sys.modules.get("typing")
        if _typing:
            new_annotations = {}
            for key, value in annotations.items():
                # Actual class used as annotation
                if (
                    value is _typing.ClassVar
                    or getattr(value, "__origin__", None) is _typing.ClassVar
                ):
                    continue
                # String used as annotation
                elif isinstance(value, str) and CLASSVAR_NAME in value:
                    continue
                else:
                    new_annotations[key] = value
            annotations = new_annotations

    annotation_names = annotations.keys()

    cls_attributes = {k: v for k, v in vars(cls).items() if isinstance(v, Attribute)}

    attribute_names = cls_attributes.keys()

    if set(annotation_names).issuperset(set(attribute_names)):
        # replace the classes' attributes dict with one with the correct
        # order from the annotations.
        new_attributes = {}
        for name in annotation_names:
            # Copy atributes that are already defined to the new dict
            # generate Attribute() values for those that are not defined.
            if hasattr(cls, name):
                if name in attribute_names:
                    new_attributes[name] = cls_attributes[name]
                else:
                    attribute_default = getattr(cls, name)
                    attrib = attribute(default=attribute_default)
                    new_attributes[name] = attrib
            else:
                attrib = attribute()
                new_attributes[name] = attrib

        cls_attributes = new_attributes

    setattr(cls, f"_{cls.__name__}_attributes", cls_attributes)

    # Remove used attributes from the class dict and annotations to match compiled behaviour
    for name in cls_attributes.keys():
        try:
            delattr(cls, name)
        except AttributeError:
            pass
        try:
            del cls.__annotations__[name]
        except (AttributeError, KeyError):
            # AttributeError as 3.9 does not guarantee the existence of __annotations__
            pass

    # Handle attributes
    attributes = {
        name: attrib
        for c in reversed(cls.__mro__)
        for name, attrib in getattr(c, f"_{c.__name__}_attributes", {}).items()
    }
    if not attributes:
        # It's easier to throw an error than to rewrite
        # The code for the useless case of a class with no attributes.
        raise LivePrefabError("Class must contain at least 1 attribute.")

    default_defined = []
    for name, attrib in attributes.items():
        if attrib.init:
            if attrib.default is not _NOTHING or attrib.default_factory is not _NOTHING:
                default_defined.append(name)
            else:
                if default_defined and not attrib.kw_only:
                    names = ", ".join(default_defined)
                    raise SyntaxError(
                        "non-default argument follows default argument",
                        f"defaults: {names}",
                        f"non_default after default: {name}",
                    )

    setattr(cls, FIELDS_ATTRIBUTE, [name for name in attributes])
    cls._attributes = attributes
    if match_args:
        cls.__match_args__ = tuple(name for name in attributes)

    if init:
        setattr(cls, "__init__", init_maker)
    else:
        setattr(cls, "__prefab_init__", prefab_init_maker)
    if repr:
        setattr(cls, "__repr__", repr_maker)
    if eq:
        setattr(cls, "__eq__", eq_maker)
    if iter:
        setattr(cls, "__iter__", iter_maker)

    return cls


# noinspection PyUnusedLocal
# @dataclass_transform(field_specifiers=(attribute, Attribute))
def prefab(
    cls: type = None,
    *,
    init=True,
    repr=True,
    eq=True,
    iter=False,
    match_args=True,
    compile_prefab=False,
    compile_fallback=False,
    compile_plain=False,
    compile_slots=False,
):
    """
    Generate boilerplate code for dunder methods in a class.

    :param cls: Class to convert to a prefab
    :param init: generates __init__ if true or __prefab_init__ if false
    :param repr: generate __repr__
    :param eq: generate __eq__
    :param iter: generate __iter__
    :param match_args: generate __match_args__

    :param compile_prefab: Direct the prefab compiler to compile this class
    :param compile_fallback: Fail with a prefab error
                             if the class has not been compiled
    :param compile_plain: Do not include the COMPILED and PREFAB_FIELDS
                          attributes after compilation
    :param compile_slots: Make the resulting compiled class use slots
    :return: class with __ methods defined
    """
    if not cls:
        # Called as () method to change defaults
        return partial(
            prefab,
            init=init,
            repr=repr,
            eq=eq,
            iter=iter,
            match_args=match_args,
            compile_prefab=compile_prefab,
            compile_fallback=compile_fallback,
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
            raise PrefabError("Slots are not supported on 'live' Prefabs.")
        else:
            # Create Live Version
            setattr(cls, COMPILED_FLAG, False)
            return _make_prefab(
                cls, init=init, repr=repr, eq=eq, iter=iter, match_args=match_args
            )
