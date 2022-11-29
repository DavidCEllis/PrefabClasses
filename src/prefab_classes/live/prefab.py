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
#
# Elements of this are taken from David Beazley's Cluegen
#
# David Beazley's Copyright from Cluegen
# ----------------------------------------------------------------------
# Classes generated from type clues.
#
#     https://github.com/dabeaz/cluegen
#
# Author: David Beazley (@dabeaz).
#         http://www.dabeaz.com
#
# Copyright (C) 2018-2021.
#
# Permission is granted to use, copy, and modify this code in any
# manner as long as this copyright message and disclaimer remain in
# the source code.  There is no warranty.  Try to use the code for the
# greater good.
# ----------------------------------------------------------------------
"""
Handle boilerplate generation for classes.

Replaces attrs.

Based on ideas (and some code) from Cluegen by David Beazley https://github.com/dabeaz/cluegen
"""
from functools import partial

# noinspection PyUnresolvedReferences
# from typing import dataclass_transform


from ..constants import FIELDS_ATTRIBUTE, COMPILED_FLAG
from ..exceptions import PrefabError, LivePrefabError, CompiledPrefabError
from .default_sentinels import _NOTHING
from .method_generators import (
    init_maker,
    repr_maker,
    eq_maker,
    iter_maker,
    prefab_init_maker,
)


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
def _make_prefab(cls: type, *, init=True, repr=True, eq=True, iter=False):
    """
    Generate boilerplate code for dunder methods in a class.

    :param cls: Class to convert to a prefab
    :param init: generate __init__
    :param repr: generate __repr__
    :param eq: generate __eq__
    :param iter: generate __iter__
    :return: class with __ methods defined
    """
    # Here first we need to look at type hints for the type hint
    # syntax variant.
    # If a key exists and is *NOT* in __annotations__ then all
    # annotations will be ignored as it becomes complex to fix the
    # ordering.
    annotation_names = getattr(cls, "__annotations__", {}).keys()
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
        except KeyError:
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
    # cls.__match_args__ = tuple(name for name in attributes)

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
            return _make_prefab(cls, init=init, repr=repr, eq=eq, iter=iter)
