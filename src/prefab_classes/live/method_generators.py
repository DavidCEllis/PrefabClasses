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

from ..constants import PRE_INIT_FUNC, POST_INIT_FUNC, PREFAB_INIT_FUNC
from .default_sentinels import _NOTHING
from .autogen import autogen


def get_init_maker(*, init_name="__init__"):
    globs = {}

    def __init__(cls):
        arglist = []
        kw_only_arglist = []
        for name, attrib in cls._attributes.items():
            if attrib.converter:
                globs[f"_{name}_converter"] = attrib.converter
            if attrib.init:
                if attrib.default is not _NOTHING:
                    if isinstance(attrib.default, (str, int, float, bool)):
                        # Just use the literal in these cases
                        arg = f"{name}={attrib.default!r}"
                    else:
                        # No guarantee repr will work for other objects
                        # so store the value in a variable and put it
                        # in the globals dict for eval
                        arg = f"{name}=_{name}_default"
                        globs[f"_{name}_default"] = attrib.default
                elif attrib.default_factory is not _NOTHING:
                    # Use NONE here and call the factory later
                    # This matches the behaviour of compiled
                    arg = f"{name}=None"
                    globs[f"_{name}_factory"] = attrib.default_factory
                else:
                    arg = name
                if attrib.kw_only:
                    kw_only_arglist.append(arg)
                else:
                    arglist.append(arg)
            # Not in init, but need to set defaults
            else:
                if attrib.default is not _NOTHING:
                    globs[f"_{name}_default"] = attrib.default
                elif attrib.default_factory is not _NOTHING:
                    globs[f"_{name}_factory"] = attrib.default_factory

        pos_args = ", ".join(arglist)
        kw_args = ", ".join(kw_only_arglist)
        if pos_args and kw_args:
            args = f"{pos_args}, *, {kw_args}"
        elif kw_args:
            args = f"*, {kw_args}"
        else:
            args = pos_args

        assignments = []
        for name, attrib in cls._attributes.items():
            if attrib.init:
                if attrib.default_factory is not _NOTHING:
                    value = f"{name} if {name} is not None else _{name}_factory()"
                else:
                    value = name
            else:
                if attrib.default_factory is not _NOTHING:
                    value = f"_{name}_factory()"
                else:
                    value = f"_{name}_default"
            if attrib.converter:
                value = f"_{name}_converter({value})"

            assignments.append((name, value))

        if hasattr(cls, PRE_INIT_FUNC):
            pre_init_call = f"    self.{PRE_INIT_FUNC}()\n"
        else:
            pre_init_call = ""

        if assignments:
            body = "\n".join(f"    self.{name} = {value}" for name, value in assignments)
        else:
            body = "    pass"

        if hasattr(cls, POST_INIT_FUNC):
            post_init_call = f"    self.{POST_INIT_FUNC}()\n"
        else:
            post_init_call = ""

        code = (
            f"def {init_name}(self, {args}):"
            f"\n{pre_init_call}\n{body}\n{post_init_call}\n"
        )

        return code

    return autogen(__init__, globs)


def get_repr_maker():
    def __repr__(cls):
        content = ", ".join(
            f"{name}={{self.{name}!r}}"
            for name, attrib in cls._attributes.items()
            if attrib.repr
        )
        code = f"def __repr__(self):\n    return f'{{type(self).__qualname__}}({content})'"
        return code

    return autogen(__repr__)


def get_eq_maker():
    def __eq__(cls):
        class_comparison = "self.__class__ is other.__class__"
        if cls._attributes:
            selfvals = ",".join(f"self.{name}" for name in cls._attributes.keys())
            othervals = ",".join(f"other.{name}" for name in cls._attributes.keys())
            instance_comparison = f"({selfvals},) == ({othervals},)"
        else:
            instance_comparison = "True"

        code = (
            f"def __eq__(self, other):\n"
            f"    return {instance_comparison} if {class_comparison} else NotImplemented\n"
        )
        return code

    return autogen(__eq__)


def get_iter_maker():
    def __iter__(cls):
        if cls._attributes:
            values = "\n".join(f"    yield self.{name} " for name in cls._attributes.keys())
        else:
            values = "    yield from ()"
        code = f"def __iter__(self):\n{values}"
        return code

    return autogen(__iter__)


init_maker = get_init_maker()
prefab_init_maker = get_init_maker(init_name=PREFAB_INIT_FUNC)
repr_maker = get_repr_maker()
eq_maker = get_eq_maker()
iter_maker = get_iter_maker()
