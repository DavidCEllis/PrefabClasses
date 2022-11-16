from pathlib import Path

from prefab_classes.compiled import preview


def test_code_result_simple():
    ex_simple = Path(__file__).parent / 'compile_targets' / 'example_simple.py'
    result = preview(ex_simple, use_black=False)
    code = (
        "from prefab_classes import prefab\n"
        "\n"
        "@prefab(compile_prefab=True, iter=True)\n"
        "class Coordinate:\n"
        "    COMPILED = True\n"
        "    PREFAB_FIELDS = ['x', 'y']\n"
        "\n"
        "    def __init__(self, x: float, y: float):\n"
        "        self.x = x\n"
        "        self.y = y\n"
        "\n"
        "    def __repr__(self):\n"
        "        return f'Coordinate(x={self.x!r}, y={self.y!r})'\n"
        "\n"
        "    def __eq__(self, other):\n"
        "        return (self.x, self.y) == (other.x, other.y) "
        "if self.__class__ == other.__class__ else NotImplemented\n"
        "\n"
        "    def __iter__(self):\n"
        "        yield self.x\n"
        "        yield self.y"
    )

    assert result == code


def test_code_result_plain():
    ex_plain = Path(__file__).parent / 'compile_targets' / 'example_plain.py'
    result = preview(ex_plain, use_black=False)
    code = (
        "from prefab_classes import prefab\n"
        "\n"
        "class Coordinate:\n"
        "\n"
        "    def __init__(self, x: float, y: float):\n"
        "        self.x = x\n"
        "        self.y = y\n"
        "\n"
        "    def __repr__(self):\n"
        "        return f'Coordinate(x={self.x!r}, y={self.y!r})'\n"
        "\n"
        "    def __eq__(self, other):\n"
        "        return (self.x, self.y) == (other.x, other.y) "
        "if self.__class__ == other.__class__ else NotImplemented"
    )

    assert result == code
