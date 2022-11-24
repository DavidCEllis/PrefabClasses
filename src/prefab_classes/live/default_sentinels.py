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

# Need a special object to provide the NOTHING feature while not matching None
# This shouldn't be used in any situation other than to compare with an is statement
# So it doesn't need any complicated properties.
_NOTHING = object()


# Special Default Classes
# When one of these is assigned to a descriptor the __set__ method
# instead stores the default value of the descriptor
class Default:
    """Base Dummy Value Class"""

    def __init__(self, value=None):
        pass


class DefaultValue(Default):
    """
    Dummy class for default values.
    This avoids the actual default value being interpreted when exec is called.
    """


class DefaultFactory(Default):
    """
    Dummy class for default factories
    """
