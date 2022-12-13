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


def autogen(func, globs=None):
    """
    Basically the cluegen function from David Beazley's cluegen
    Modified slightly due to other changes.

    Using this as a decorator indicates that the function will return a string
    which should be used to replace the function itself for that specific class.
    """
    # globs can be a given empty dict, so specifically check for None.
    globs = globs if globs is not None else {}

    def __get__(self, instance, cls):
        # Include the defaultvalue class used as a placeholder for defaults
        local_vars = {}
        code = func(cls)
        exec(code, globs, local_vars)
        # Having executed the code, the method should now exist
        # and can be retrieved by name from the dict
        method = local_vars[func.__name__]
        method.__qualname__ = f"{cls.__qualname__}.{method.__name__}"
        # Replace the attribute with the real function - this will only be called once.
        setattr(cls, func.__name__, method)
        return method.__get__(instance, cls)

    return type(f"AutoGen_{func.__name__}", (), dict(__get__=__get__))()
