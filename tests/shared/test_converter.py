from pathlib import Path


def test_converter(importer):
    from converter import SystemPath

    assert SystemPath.COMPILED == importer

    pth = SystemPath("fake/directory")

    assert pth.path == Path("fake/directory")


def test_default_converter(importer):
    """Check the converter works on default arguments"""

    from converter import SystemPathDefault

    assert SystemPathDefault.COMPILED == importer

    pth = SystemPathDefault()

    assert pth.path == Path("fake/directory")


def test_converter_only_init(importer):
    """Check the converter only runs on init"""

    from converter import SystemPath

    assert SystemPath.COMPILED == importer

    pth = SystemPath("fake/directory")

    assert pth.path == Path("fake/directory")

    pth.path = "alternate/directory"

    assert pth.path == "alternate/directory"  # This has not been converted to a path.


def test_convert_twice(importer):
    from converter import SystemPath

    pth = SystemPath("fake/directory")
    pth2 = SystemPath("fake/directory")

    assert pth2.path == Path("fake/directory")
