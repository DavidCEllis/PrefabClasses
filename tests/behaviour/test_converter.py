"""Test the converter parameter works as intended"""
from pathlib import Path

from prefab_classes import prefab, attribute


def test_converter():

    @prefab
    class SystemPath:
        path = attribute(converter=Path)

    pth = SystemPath('fake/directory')

    assert pth.path == Path('fake/directory')


def test_default_converter():
    """Check the converter works on default arguments"""

    @prefab
    class SystemPath:
        path = attribute(default='fake/directory', converter=Path)

    pth = SystemPath()

    assert pth.path == Path('fake/directory')


def test_converter_only_init():
    """Check the converter only runs on init"""

    @prefab
    class SystemPath:
        path = attribute(converter=Path)

    pth = SystemPath('fake/directory')

    assert pth.path == Path('fake/directory')

    pth.path = 'alternate/directory'

    assert pth.path == 'alternate/directory'  # This has not been converted to a path.
