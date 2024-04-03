# ==============================================================================
# Copyright (c) 2022-2024 David C Ellis
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

try:
    from _collections_abc import Mapping
except ImportError:
    from collections.abc import Mapping


# False imports for typing dataclass transform and implementation otherwise
# The 'typing' import takes over 2x as long as importing this entire module
# So the impact on import time of the typing import is unacceptable.
# noinspection PyUnreachableCode
if False:
    try:
        from typing import dataclass_transform
    except ImportError:
        from typing_extensions import dataclass_transform
else:

    def dataclass_transform(
        *,
        eq_default: bool = True,
        order_default: bool = False,
        kw_only_default: bool = False,
        frozen_default: bool = False,
        field_specifiers: tuple = (),
        **kwargs,
    ):
        def decorator(cls_or_fn):
            cls_or_fn.__dataclass_transform__ = {
                "eq_default": eq_default,
                "order_default": order_default,
                "kw_only_default": kw_only_default,
                "frozen_default": frozen_default,
                "field_specifiers": field_specifiers,
                "kwargs": kwargs,
            }
            return cls_or_fn

        return decorator


from ._shared import (
    FIELDS_ATTRIBUTE,
    CLASSVAR_NAME,
    PRE_INIT_FUNC,
    POST_INIT_FUNC,
    INTERNAL_DICT,
)
from ._shared import PrefabError
from ._shared import NOTHING, KW_ONLY

from ._method_generators import (
    init_maker,
    repr_maker,
    repr_maker_no_eval,
    eq_maker,
    iter_maker,
    prefab_init_maker,
    frozen_setattr_maker,
    frozen_delattr_maker,
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


class Attribute:
    __slots__ = (
        "default",
        "default_factory",
        "init",
        "repr",
        "compare",
        "kw_only",
        "exclude_field",
        "doc",
        "_type",
    )
    __match_args__ = (
        "default",
        "default_factory",
        "init",
        "repr",
        "compare",
        "kw_only",
        "exclude_field",
        "doc",
        "_type",
    )
    init: bool
    repr: bool
    compare: bool
    kw_only: bool
    exclude_field: bool
    doc: str | None

    def __init__(
        self,
        *,
        default=NOTHING,
        default_factory=NOTHING,
        init: bool = True,
        repr: bool = True,
        compare: bool = True,
        kw_only: bool = False,
        exclude_field: bool = False,
        doc: str | None = None,
        type=NOTHING,
    ):

        if kw_only and (not init):
            raise PrefabError("Attribute cannot be keyword only if it is not in init.")
        if default is not NOTHING and default_factory is not NOTHING:
            raise PrefabError(
                "Cannot define both a default value and a default factory."
            )

        self.default = default
        self.default_factory = default_factory
        self.init = init
        self.repr = repr
        self.compare = compare
        self.kw_only = kw_only
        self.exclude_field = exclude_field
        self.doc = doc
        self._type = type

    def __repr__(self):
        return (
            f"{type(self).__qualname__}("
            f"default={self.default!r}, "
            f"default_factory={self.default_factory!r}, "
            f"init={self.init!r}, "
            f"repr={self.repr!r}, "
            f"compare={self.compare!r}, "
            f"kw_only={self.kw_only!r}, "
            f"exclude_field={self.exclude_field!r},"
            f"doc={self.doc!r},"
            f"type={self._type!r},"
            f")"
        )

    def __eq__(self, other):
        return (
            (
                self.default,
                self.default_factory,
                self.init,
                self.repr,
                self.compare,
                self.kw_only,
                self.exclude_field,
                self.doc,
                self._type,
            )
            == (
                other.default,
                other.default_factory,
                other.init,
                other.repr,
                other.compare,
                other.kw_only,
                other.exclude_field,
                other.doc,
                other._type,
            )
            if self.__class__ == other.__class__
            else NotImplemented
        )


def attribute(
    *,
    default=NOTHING,
    default_factory=NOTHING,
    init=True,
    repr=True,
    compare=True,
    kw_only=False,
    exclude_field=False,
    doc=None,
    type=NOTHING,
):
    """
    Additional definition for how to generate standard methods
    for an instance attribute.

    :param default: Default value for this attribute
    :param default_factory: 0 argument callable to give a default value
                            (for otherwise mutable defaults, eg: list)
    :param init: Include this attribute in the __init__ parameters
    :param repr: Include this attribute in the class __repr__
    :param compare: Include this attribute in the class __eq__
    :param kw_only: Make this argument keyword only in init
    :param exclude_field: Exclude this field from all magic method generation
                          apart from __init__
                          and do not include it in PREFAB_FIELDS
    :param doc: Parameter documentation for slotted classes
    :param type: Type of this attribute (for slotted classes)

    :return: Attribute generated with these parameters.
    """
    return Attribute(
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        compare=compare,
        kw_only=kw_only,
        exclude_field=exclude_field,
        doc=doc,
        type=type,
    )


class SlotAttributes(Mapping):
    """
    A special mapping class to define slots for a slotted prefab.
    """

    def __init__(self, **attributes):
        self._attributes = attributes

    def __getitem__(self, item):
        return self._attributes[item]

    def __len__(self):
        return len(self._attributes)

    def __iter__(self):
        yield from self._attributes


def _make_prefab(
    cls: type,
    *,
    init=True,
    repr=True,
    eq=True,
    iter=False,
    match_args=True,
    kw_only=False,
    frozen=False,
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
    :param frozen: Prevent attribute values from being changed once defined
                   (This does not prevent the modification of mutable attributes
                   such as lists)
    :return: class with __ methods defined
    """
    # Check if the class has already been processed
    if cls.__dict__.get(INTERNAL_DICT) is not None:
        raise PrefabError(
            f"Decorated class {cls.__name__!r} "
            f"has already been processed as a Prefab."
        )

    # Make the internals dict
    prefab_internals = {}
    setattr(cls, INTERNAL_DICT, prefab_internals)

    # Check for slots first
    # If provided as a SlotAttributes instance this will be used
    # regardless of other data
    cls_slots = getattr(cls, "__slots__", None)

    # We need to look at type hints for the type hint
    # syntax variant.
    # If a key exists and is *NOT* in __annotations__ then all
    # annotations will be ignored as it becomes complex to fix the
    # ordering.
    cls_annotations = getattr(cls, "__annotations__", {})

    cls_annotation_names = cls_annotations.keys()

    if isinstance(cls_slots, SlotAttributes):
        prefab_internals["slotted"] = True

        # If slots are defined we must use slots
        cls_attributes = {}
        slot_replacement = {}
        updated_types = {}

        for k, v in cls_slots.items():
            if isinstance(v, Attribute):
                attrib = v
                if v._type is not NOTHING:
                    updated_types[k] = attrib._type
            else:
                # Plain values treated as defaults
                attrib = attribute(default=v)

            if kw_only:
                attrib.kw_only = True

            slot_replacement[k] = attrib.doc
            cls_attributes[k] = attrib

        # Replace the SlotAttributes instance with a regular dict
        # So that help() works
        # This also prevents subclasses from unintentionally reusing the slots
        # If they do not declare their own slots.
        setattr(cls, "__slots__", slot_replacement)
        # Update annotations with any types from the slots assignment
        cls_annotations.update(updated_types)
        setattr(cls, "__annotations__", cls_annotations)
    else:
        prefab_internals["slotted"] = False

        cls_attributes = {
            k: v for k, v in vars(cls).items() if isinstance(v, Attribute)
        }

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
                        raise PrefabError(
                            "Class can not be defined as keyword only twice"
                        )
                    kw_flag = True
                else:
                    # Copy atributes that are already defined to the new dict
                    # generate Attribute() values for those that are not defined.
                    if cls_slots is None:
                        cls_slots = {}

                    if hasattr(cls, name) and name not in cls_slots:
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

            cls_attributes = new_attributes
        else:
            for name, attrib in cls_attributes.items():
                if kw_only:
                    attrib.kw_only = True

                delattr(cls, name)
                # Some items can still be annotated.
                try:
                    attrib._type = cls_annotations[name]
                except KeyError:
                    pass

    prefab_internals["local_attributes"] = cls_attributes

    mro = cls.__mro__[:-1]  # skip 'object' base class

    # Handle inheritance
    if mro == (cls,):  # special case of no inheritance.
        attributes = cls_attributes.copy()
    else:
        attributes = {}
        for c in reversed(mro):
            try:
                attributes.update(getattr(c, INTERNAL_DICT)["local_attributes"])
            except AttributeError:
                pass

    # Check pre_init and post_init functions if they exist
    try:
        func = getattr(cls, PRE_INIT_FUNC)
        func_code = func.__code__
    except AttributeError:
        pass
    else:
        if func_code.co_posonlyargcount > 0:
            raise PrefabError(
                "Positional only arguments are not supported in pre or post init functions."
            )

        argcount = func_code.co_argcount + func_code.co_kwonlyargcount

        # Include the first argument if the method is static
        is_static = type(cls.__dict__.get(PRE_INIT_FUNC)) is staticmethod

        arglist = (
            func_code.co_varnames[:argcount]
            if is_static
            else func_code.co_varnames[1:argcount]
        )

        for item in arglist:
            if item not in attributes.keys():
                raise PrefabError(
                    f"{item} argument in __prefab_pre_init__ is not a valid attribute."
                )

    post_init_args = []
    try:
        func = getattr(cls, POST_INIT_FUNC)
        func_code = func.__code__
    except AttributeError:
        pass
    else:
        if func_code.co_posonlyargcount > 0:
            raise PrefabError(
                "Positional only arguments are not supported in pre or post init functions."
            )

        argcount = func_code.co_argcount + func_code.co_kwonlyargcount

        # Include the first argument if the method is static
        is_static = type(cls.__dict__.get(POST_INIT_FUNC)) is staticmethod

        arglist = (
            func_code.co_varnames[:argcount]
            if is_static
            else func_code.co_varnames[1:argcount]
        )

        for item in arglist:
            if item not in attributes.keys():
                raise PrefabError(
                    f"{item} argument in __prefab_post_init__ is not a valid attribute."
                )

        post_init_args.extend(arglist)

    default_defined = []
    valid_fields = []

    use_eval_repr = True

    for name, attrib in attributes.items():
        if use_eval_repr and (attrib.exclude_field or (attrib.init ^ attrib.repr)):
            use_eval_repr = False

        if attrib.exclude_field:
            if name not in post_init_args:
                raise PrefabError(
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
    prefab_internals["attributes"] = attributes

    if match_args and "__match_args__" not in cls.__dict__:
        setattr(cls, "__match_args__", tuple(valid_fields))

    if init and "__init__" not in cls.__dict__:
        setattr(cls, "__init__", init_maker)
    else:
        setattr(cls, "__prefab_init__", prefab_init_maker)
    if repr and "__repr__" not in cls.__dict__:
        if use_eval_repr:
            setattr(cls, "__repr__", repr_maker)
        else:
            setattr(cls, "__repr__", repr_maker_no_eval)
    if eq and "__eq__" not in cls.__dict__:
        setattr(cls, "__eq__", eq_maker)
    if iter and "__iter__" not in cls.__dict__:
        setattr(cls, "__iter__", iter_maker)
    if frozen:
        setattr(cls, "__setattr__", frozen_setattr_maker)
        setattr(cls, "__delattr__", frozen_delattr_maker)

    return cls


@dataclass_transform(field_specifiers=(attribute,))
def prefab(
    cls=None,
    *,
    init=True,
    repr=True,
    eq=True,
    iter=False,
    match_args=True,
    kw_only=False,
    frozen=False,
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
    :param frozen: Prevent attribute values from being changed once defined
                   (This does not prevent the modification of mutable attributes such as lists)

    :return: class with __ methods defined
    """
    if not cls:
        # Called as () method to change defaults
        return lambda cls_: prefab(
            cls_,
            init=init,
            repr=repr,
            eq=eq,
            iter=iter,
            match_args=match_args,
            kw_only=kw_only,
            frozen=frozen,
        )
    else:
        return _make_prefab(
            cls,
            init=init,
            repr=repr,
            eq=eq,
            iter=iter,
            match_args=match_args,
            kw_only=kw_only,
            frozen=frozen,
        )


def build_prefab(
    class_name: str,
    attributes: list[tuple[str, Attribute]],
    *,
    bases: tuple[type, ...] = (),
    class_dict: None | dict[str, object] = None,
    init=True,
    repr=True,
    eq=True,
    iter=False,
    match_args=True,
    kw_only=False,
    frozen=False,
):
    """
    Dynamically construct a (dynamic) prefab.

    :param class_name: name of the resulting prefab class
    :param attributes: list of (name, attribute()) pairs to assign to the class
                       for construction
    :param bases: Base classes to inherit from
    :param class_dict: Other values to add to the class dictionary on creation
                       This is the 'dict' parameter from 'type'
    :param init: generates __init__ if true or __prefab_init__ if false
    :param repr: generate __repr__
    :param eq: generate __eq__
    :param iter: generate __iter__
    :param match_args: generate __match_args__
    :param kw_only: make all attributes keyword only
    :param frozen: Prevent attribute values from being changed once defined
                   (This does not prevent the modification of mutable attributes such as lists)
    :return: class with __ methods defined
    """
    class_dict = {} if class_dict is None else class_dict
    cls = type(class_name, bases, class_dict)
    for name, attrib in attributes:
        setattr(cls, name, attrib)

    cls = _make_prefab(
        cls,
        init=init,
        repr=repr,
        eq=eq,
        iter=iter,
        match_args=match_args,
        kw_only=kw_only,
        frozen=frozen,
    )

    return cls
