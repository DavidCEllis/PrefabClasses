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

from ducktools.lazyimporter import LazyImporter, FromImport

from ._shared import (
    PRE_INIT_FUNC,
    POST_INIT_FUNC,
    PREFAB_INIT_FUNC,
    FIELDS_ATTRIBUTE,
    INTERNAL_DICT,
    NOTHING,
)

_laz = LazyImporter([FromImport("reprlib", "recursive_repr")])


def autogen(func):
    """
    Basically the cluegen function from David Beazley's cluegen
    Modified slightly due to other changes.

    Using this as a decorator indicates that the function will return a string
    which should be used to replace the function itself for that specific class.
    """

    def __get__(self, instance, cls):
        local_vars = {}
        code, globs = func(cls)
        exec(code, globs, local_vars)
        # Having executed the code, the method should now exist
        # and can be retrieved by name from the dict
        method = local_vars[func.__name__]
        method.__qualname__ = f"{cls.__qualname__}.{method.__name__}"
        # Replace the attribute with the real function - this will only be called once.
        setattr(cls, func.__name__, method)

        return method.__get__(instance, cls)

    return type(f"AutoGen_{func.__name__}", (), dict(__get__=__get__))()


def get_init_maker(*, init_name="__init__"):
    def __init__(cls):
        globs = {}
        # Get the internals dictionary and prepare attributes
        internals = getattr(cls, INTERNAL_DICT)
        attributes = internals["attributes"]

        # Handle pre/post init first - post_init can change types for __init__
        # Get pre and post init arguments
        pre_init_args = []
        post_init_args = []
        post_init_annotations = {}

        for func_name, func_arglist in [
            (PRE_INIT_FUNC, pre_init_args),
            (POST_INIT_FUNC, post_init_args),
        ]:
            try:
                func = getattr(cls, func_name)
                func_code = func.__code__
            except AttributeError:
                pass
            else:
                argcount = func_code.co_argcount + func_code.co_kwonlyargcount

                # Identify if method is static, if so include first arg, otherwise skip
                is_static = type(cls.__dict__.get(func_name)) is staticmethod

                arglist = (
                    func_code.co_varnames[:argcount]
                    if is_static
                    else func_code.co_varnames[1:argcount]
                )

                func_arglist.extend(arglist)

                if func_name == POST_INIT_FUNC:
                    post_init_annotations.update(func.__annotations__)

        pos_arglist = []
        kw_only_arglist = []
        for name, attrib in attributes.items():
            # post_init annotations can be used to broaden types.
            if name in post_init_annotations:
                globs[f"_{name}_type"] = post_init_annotations[name]
            elif attrib._type is not NOTHING:
                globs[f"_{name}_type"] = attrib._type

            if attrib.init:
                if attrib.default is not NOTHING:
                    if isinstance(attrib.default, (str, int, float, bool)):
                        # Just use the literal in these cases
                        if attrib._type is NOTHING:
                            arg = f"{name}={attrib.default!r}"
                        else:
                            arg = f"{name}: _{name}_type = {attrib.default!r}"
                    else:
                        # No guarantee repr will work for other objects
                        # so store the value in a variable and put it
                        # in the globals dict for eval
                        if attrib._type is NOTHING:
                            arg = f"{name}=_{name}_default"
                        else:
                            arg = f"{name}: _{name}_type = _{name}_default"
                        globs[f"_{name}_default"] = attrib.default
                elif attrib.default_factory is not NOTHING:
                    # Use NONE here and call the factory later
                    # This matches the behaviour of compiled
                    if attrib._type is NOTHING:
                        arg = f"{name}=None"
                    else:
                        arg = f"{name}: _{name}_type = None"
                    globs[f"_{name}_factory"] = attrib.default_factory
                else:
                    if attrib._type is NOTHING:
                        arg = name
                    else:
                        arg = f"{name}: _{name}_type"
                if attrib.kw_only:
                    kw_only_arglist.append(arg)
                else:
                    pos_arglist.append(arg)
            # Not in init, but need to set defaults
            else:
                if attrib.default is not NOTHING:
                    globs[f"_{name}_default"] = attrib.default
                elif attrib.default_factory is not NOTHING:
                    globs[f"_{name}_factory"] = attrib.default_factory

        pos_args = ", ".join(pos_arglist)
        kw_args = ", ".join(kw_only_arglist)
        if pos_args and kw_args:
            args = f"{pos_args}, *, {kw_args}"
        elif kw_args:
            args = f"*, {kw_args}"
        else:
            args = pos_args

        assignments = []
        processes = []  # post_init values still need default factories to be called.
        for name, attrib in attributes.items():
            if attrib.init:
                if attrib.default_factory is not NOTHING:
                    value = f"{name} if {name} is not None else _{name}_factory()"
                else:
                    value = name
            else:
                if attrib.default_factory is not NOTHING:
                    value = f"_{name}_factory()"
                elif attrib.default is not NOTHING:
                    value = f"_{name}_default"
                else:
                    value = None

            if name in post_init_args:
                if attrib.default_factory is not NOTHING:
                    processes.append((name, value))
            elif value is not None:
                assignments.append((name, value))

        if hasattr(cls, PRE_INIT_FUNC):
            pre_init_arg_call = ", ".join(f"{name}={name}" for name in pre_init_args)
            pre_init_call = f"    self.{PRE_INIT_FUNC}({pre_init_arg_call})\n"
        else:
            pre_init_call = ""

        if assignments or processes:
            body = ""
            body += "\n".join(
                f"    self.{name} = {value}" for name, value in assignments
            )
            body += "\n"
            body += "\n".join(f"    {name} = {value}" for name, value in processes)
        else:
            body = "    pass"

        if hasattr(cls, POST_INIT_FUNC):
            post_init_arg_call = ", ".join(f"{name}={name}" for name in post_init_args)
            post_init_call = f"    self.{POST_INIT_FUNC}({post_init_arg_call})\n"
        else:
            post_init_call = ""

        code = (
            f"def {init_name}(self, {args}):\n"
            f"{pre_init_call}\n"
            f"{body}\n"
            f"{post_init_call}\n"
        )
        return code, globs

    return autogen(__init__)


def get_repr_maker(will_eval=True):
    def __repr__(cls):
        internals = getattr(cls, INTERNAL_DICT)
        attributes = internals["attributes"]
        content = ", ".join(
            f"{name}={{self.{name}!r}}"
            for name, attrib in attributes.items()
            if attrib.repr and not attrib.exclude_field
        )
        if will_eval:
            code = (
                f"@_laz.recursive_repr()\n"
                f"def __repr__(self):\n"
                f"    return f'{{type(self).__qualname__}}({content})'\n"
            )
        else:
            if content:
                code = (
                    f"@_laz.recursive_repr()\n"
                    f"def __repr__(self):\n"
                    f"    return f'<prefab {{type(self).__qualname__}}; {content}>'\n"
                )
            else:
                code = (
                    f"@_laz.recursive_repr()\n"
                    f"def __repr__(self):\n"
                    f"    return f'<prefab {{type(self).__qualname__}}>'\n"
                )

        globs = {"_laz": _laz}

        return code, globs

    return autogen(__repr__)


def get_eq_maker():
    def __eq__(cls):
        class_comparison = "self.__class__ is other.__class__"
        field_names = getattr(cls, FIELDS_ATTRIBUTE)
        if field_names:
            selfvals = ",".join(f"self.{name}" for name in field_names)
            othervals = ",".join(f"other.{name}" for name in field_names)
            instance_comparison = f"({selfvals},) == ({othervals},)"
        else:
            instance_comparison = "True"

        code = (
            f"def __eq__(self, other):\n"
            f"    return {instance_comparison} if {class_comparison} else NotImplemented\n"
        )
        globs = {}

        return code, globs

    return autogen(__eq__)


def get_iter_maker():
    def __iter__(cls):
        field_names = getattr(cls, FIELDS_ATTRIBUTE)
        if field_names:
            values = "\n".join(f"    yield self.{name} " for name in field_names)
        else:
            values = "    yield from ()"
        code = f"def __iter__(self):\n{values}"
        globs = {}
        return code, globs

    return autogen(__iter__)


def get_frozen_setattr_maker():
    def __setattr__(cls):
        globs = {}
        field_names = getattr(cls, FIELDS_ATTRIBUTE)

        # Make the fields set literal
        fields_delimited = ", ".join(f"{field!r}" for field in field_names)
        field_set = f"{{ {fields_delimited} }}"

        if getattr(cls, INTERNAL_DICT)["slotted"]:
            globs["__prefab_setattr_func"] = object.__setattr__
            setattr_method = "__prefab_setattr_func(self, name, value)"
        else:
            setattr_method = "self.__dict__[name] = value"

        body = (
            f"    if hasattr(self, name) or name not in {field_set}:\n"
            f'        raise TypeError("{cls.__name__!r} object does not support attribute assignment")\n'
            f"    else:\n"
            f"        {setattr_method}\n"
        )
        code = f"def __setattr__(self, name, value):\n{body}"

        return code, globs

    # Pass the exception to exec
    return autogen(__setattr__)


def get_frozen_delattr_maker():
    def __delattr__(cls):
        body = f'    raise TypeError("{cls.__name__!r} object does not support attribute deletion")\n'
        code = f"def __delattr__(self, name):\n{body}"
        globs = {}
        return code, globs

    return autogen(__delattr__)


init_maker = get_init_maker()
prefab_init_maker = get_init_maker(init_name=PREFAB_INIT_FUNC)
repr_maker = get_repr_maker(will_eval=True)
repr_maker_no_eval = get_repr_maker(will_eval=False)
eq_maker = get_eq_maker()
iter_maker = get_iter_maker()
frozen_setattr_maker = get_frozen_setattr_maker()
frozen_delattr_maker = get_frozen_delattr_maker()
