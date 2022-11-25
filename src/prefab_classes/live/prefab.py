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
from typing import dataclass_transform


from ..constants import FIELDS_ATTRIBUTE, COMPILED_FLAG
from ..exceptions import PrefabError, LivePrefabError, CompiledPrefabError
from .default_sentinels import DefaultFactory, DefaultValue, _NOTHING
from .method_generators import (
    init_maker,
    repr_maker,
    eq_maker,
    iter_maker,
    prefab_init_maker,
)


class Attribute:
    """
    Descriptor class to define attributes.

    This replaces the use of type hints in cluegen.
    """

    # noinspection PyProtectedMember
    def __set_name__(self, owner, name):
        # Here we append any generated attributes to a private variable
        # This will be used instead of cluegen's all_clues.

        # Make a new list for this class if it doesn't exist.
        # The class name is used to avoid sharing a list with a parent class.
        attribute_var = f"_{owner.__name__}_attributes"

        try:
            sub_attributes = getattr(owner, attribute_var)
        except AttributeError:
            sub_attributes = {}
            setattr(owner, attribute_var, sub_attributes)

        sub_attributes[name] = self

        self.private_name = f"_prefab_attribute_{name}"

    def __get__(self, obj, objtype=None):
        # The default values here should only be used in the __init__ method
        # This means that for a factory all it needs to know is that the default
        # is a factory and not its value. So the default return for factory
        # Attributes is DefaultFactory() and NOT self.default_factory().
        # The actual value is set during __init__.
        if self.default is not _NOTHING:
            return getattr(obj, self.private_name, self.default)
        if self.default_factory is not _NOTHING:
            # noinspection PyCallingNonCallable
            return getattr(obj, self.private_name, DefaultFactory())
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        # Detect if the value is a default placeholder and replace
        # it with the real value.
        if isinstance(value, DefaultValue):
            value = self.default
        elif isinstance(value, DefaultFactory):
            # noinspection PyCallingNonCallable
            value = self.default_factory()
        if self.converter and not self._converted:
            self._converted = True
            value = self.converter(value)
        setattr(obj, self.private_name, value)

    # noinspection PyShadowingBuiltins
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
        Create an Attribute for a prefab
        :param default: Default value for this attribute
        :param default_factory: No argument callable to give a default value (for otherwise mutable defaults)
        :param converter: prefab.attr = x -> prefab.attr = converter(x)
        :param init: Include this attribute in the __init__ parameters
        :param repr: Include this attribute in the class __repr__
        :param kw_only: Make this argument keyword only in init
        """
        if not init and default is _NOTHING and default_factory is _NOTHING:
            raise LivePrefabError(
                "Must provide a default value/factory if the attribute is not in init."
            )
        if default is not _NOTHING and default_factory is not _NOTHING:
            raise LivePrefabError(
                "Cannot define both a default value and a default factory."
            )
        if kw_only and not init:
            raise LivePrefabError("Attribute cannot be keyword only if it is not in init.")

        self.default = default
        self.default_factory = default_factory

        self.converter = converter
        self._converted = False

        self.init = init
        self.repr = repr
        self.kw_only = kw_only


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
    Get an Attribute instance - indirect to allow for potential changes in the future

    :param default: Default value for this attribute
    :param default_factory: No argument callable to give a default value (for otherwise mutable defaults)
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


@dataclass_transform(field_specifiers=(attribute, Attribute))
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
    cls_attributes = getattr(cls, f"_{cls.__name__}_attributes", {})
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
                    # Set private_name because set_name is never called
                    attrib.private_name = f"_prefab_attribute_{name}"
                    setattr(cls, name, attrib)
                    new_attributes[name] = attrib
            else:
                attrib = attribute()
                # Set private_name because set_name is never called
                attrib.private_name = f"_prefab_attribute_{name}"
                setattr(cls, name, attrib)
                new_attributes[name] = attrib

        setattr(cls, f"_{cls.__name__}_attributes", new_attributes)

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
@dataclass_transform(field_specifiers=(attribute, Attribute))
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
):
    """
    Generate boilerplate code for dunder methods in a class.

    :param cls: Class to convert to a prefab
    :param init: generates __init__ if true or __prefab_init__ if false
    :param repr: generate __repr__
    :param eq: generate __eq__
    :param iter: generate __iter__

    :param compile_prefab: Direct the prefab compiler to compile this class
    :param compile_fallback: Fail with a prefab error if the class has not been compiled
    :param compile_plain: Do not include the COMPILED and PREFAB_FIELDS attributes after compilation
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
        else:
            # Create Live Version
            setattr(cls, COMPILED_FLAG, False)
            return _make_prefab(cls, init=init, repr=repr, eq=eq, iter=iter)
