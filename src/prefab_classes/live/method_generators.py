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

from .default_sentinels import _NOTHING, DefaultFactory
from .autogen import autogen


def get_init_maker():
    def __init__(cls):
        arglist = []
        kw_only_arglist = []
        for name, attrib in cls._attributes.items():
            if attrib.init:
                if hasattr(cls, name):
                    attr_value = getattr(cls, name)
                    if isinstance(attr_value, (str, int, float, bool)):
                        arg = f'{name}={attr_value!r}'
                    elif isinstance(attr_value, DefaultFactory):
                        # factory values will specifically return defaultfactory
                        arg = f'{name}=DefaultFactory("{name}")'
                    else:
                        arg = f'{name}=DefaultValue("{name}")'
                else:
                    arg = name
                if attrib.kw_only:
                    kw_only_arglist.append(arg)
                else:
                    arglist.append(arg)
        pos_args = ', '.join(arglist)
        kw_args = ', '.join(kw_only_arglist)
        if pos_args and kw_args:
            args = f"{pos_args}, *, {kw_args}"
        elif kw_args:
            args = f"*, {kw_args}"
        else:
            args = pos_args

        assignments = (
            (name, name)
            if attrib.init
            else (name, f'DefaultValue("{name}")')
            if attrib.default is not _NOTHING
            else (name, f'DefaultFactory("{name}")')
            for name, attrib in cls._attributes.items()
        )
        body = '\n'.join(
            f"    self.{name} = {value}"
            for name, value in assignments
        )

        code = f"def __init__(self, {args}):\n{body}\n"
        return code
    return autogen(__init__)


def get_repr_maker():
    def __repr__(cls):
        content = ', '.join(
            f"{name}={{self.{name}!r}}"
            for name, attrib in cls._attributes.items()
            if attrib.repr
        )
        code = f"def __repr__(self):\n    return f'{{type(self).__name__}}({content})'"
        return code
    return autogen(__repr__)


def get_eq_maker():
    def __eq__(cls):
        selfvals = ','.join(f'self.{name}' for name in cls._attributes.keys())
        othervals = ','.join(f'other.{name}' for name in cls._attributes.keys())
        class_comparison = "self.__class__ is other.__class__"
        instance_comparison = f"({selfvals},) == ({othervals},)"
        code = (
            f"def __eq__(self, other):\n"
            f"    return {instance_comparison} if {class_comparison} else NotImplemented\n"
        )
        return code
    return autogen(__eq__)


def get_iter_maker():
    def __iter__(cls):
        values = '\n'.join(f'    yield self.{name} ' for name in cls._attributes.keys())
        code = f"def __iter__(self):\n{values}"
        return code
    return autogen(__iter__)
