"""Test the converter parameter works as intended"""
from pathlib import Path

from prefab_classes import prefab, Attribute


def test_converter():

    @prefab
    class SystemPath:
        path = Attribute(converter=Path)

    pth = SystemPath('fake/directory')

    assert pth.path == Path('fake/directory')


def test_default_converter():
    """Check the converter works on default arguments"""

    @prefab
    class SystemPath:
        path = Attribute(default='fake/directory', converter=Path)

    pth = SystemPath()

    assert pth.path == Path('fake/directory')


def test_converter_only_init():
    """Check the converter only runs on init"""

    @prefab
    class SystemPath:
        path = Attribute(converter=Path)

    pth = SystemPath('fake/directory')

    assert pth.path == Path('fake/directory')

    pth.path = 'alternate/directory'

    assert pth.path == 'alternate/directory'  # This has not been converted to a path.


def test_converter_always():
    """Check the converter runs every time if told to"""

    @prefab
    class SystemPath:
        path = Attribute(converter=Path, always_convert=True)

    pth = SystemPath('fake/directory')

    assert pth.path == Path('fake/directory')

    pth.path = 'alternate/directory'

    assert pth.path == Path('alternate/directory')  # This has not been converted to a path.
