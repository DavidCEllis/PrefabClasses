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
from ..exceptions import PrefabError
from .default_sentinels import DefaultFactory, DefaultValue, _NOTHING
from .method_generators import init_maker, repr_maker, eq_maker, iter_maker

prefab_register = {}


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
        attribute_var = f'_{owner.__name__}_attributes'
        sub_attributes = getattr(owner, attribute_var, {})
        sub_attributes[name] = self
        setattr(owner, attribute_var, sub_attributes)

        self.private_name = f'_prefab_attribute_{name}'

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
        if self.converter and (self._converter_unused or self.always_convert):
            self._converter_unused = False
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
            always_convert=False
    ):
        """
        Create an Attribute for a prefab
        :param default: Default value for this attribute
        :param default_factory: No argument callable to give a default value (for otherwise mutable defaults)
        :param converter: prefab.attr = x -> prefab.attr = converter(x)
        :param init: Include this attribute in the __init__ parameters
        :param repr: Include this attribute in the class __repr__
        :param kw_only: Make this argument keyword only in init
        :param always_convert: Run the converter whenever the argument is set, not just in init
        """
        if not init and default is _NOTHING and default_factory is _NOTHING:
            raise PrefabError("Must provide a default value/factory if the attribute is not in init.")
        if default is not _NOTHING and default_factory is not _NOTHING:
            raise PrefabError("Cannot define both a default value and a default factory.")
        if kw_only and not init:
            raise PrefabError("Attribute cannot be keyword only if it is not in init.")

        self.default = default
        self.default_factory = default_factory

        self.converter = converter
        self.always_convert = always_convert
        self._converter_unused = True

        self.init = init
        self.repr = repr
        self.kw_only = kw_only


def prefab(cls: type):
    if cls.__qualname__ in prefab_register:
        raise PrefabError(
            f"Class with name {cls.__qualname__} "
            f"already registered as a prefab."
        )
    # Here first we need to look at type hints for the type hint
    # syntax variant.
    # If a key exists and is *NOT* in __annotations__ then all
    # annotations will be ignored as it becomes complex to fix the
    # ordering.
    annotation_names = getattr(cls, '__annotations__', {}).keys()
    cls_attributes = getattr(cls, f'_{cls.__name__}_attributes', {})
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
                    attribute = Attribute(default=attribute_default)
                    # Set private_name because set_name is never called
                    attribute.private_name = f'_prefab_attribute_{name}'
                    setattr(cls, name, attribute)
                    new_attributes[name] = attribute
            else:
                attribute = Attribute()
                # Set private_name because set_name is never called
                attribute.private_name = f'_prefab_attribute_{name}'
                setattr(cls, name, attribute)
                new_attributes[name] = attribute

        setattr(cls, f'_{cls.__name__}_attributes', new_attributes)

    # Handle attributes
    attributes = {name: attrib for c in reversed(cls.__mro__)
                  for name, attrib in getattr(c, f'_{c.__name__}_attributes', {}).items()}
    if not attributes:
        # It's easier to throw an error than to rewrite
        # The code for the useless case of a class with no attributes.
        raise PrefabError("Class must contain at least 1 attribute.")

    default_defined = []
    for name, attrib in attributes.items():
        if attrib.default is not _NOTHING or attrib.default_factory is not _NOTHING:
            default_defined.append(name)
        else:
            if default_defined:
                names = ', '.join(default_defined)
                raise SyntaxError(
                    "non-default argument follows default argument",
                    f"defaults: {names}",
                    f"non_default after default: {name}"
                )

    cls._attributes = attributes
    cls.__match_args__ = tuple(name for name in attributes)

    setattr(cls, '__init__', init_maker)
    setattr(cls, '__repr__', repr_maker)
    setattr(cls, '__eq__', eq_maker)
    setattr(cls, '__iter__', iter_maker)

    prefab_register[cls.__qualname__] = cls
    return cls
