from pathlib import Path

from prefab_classes.compiled import preview, rewrite_code


def test_code_result_simple():
    ex_simple = Path(__file__).parent / "compile_targets" / "example_simple.py"
    result = preview(ex_simple, use_black=False)
    code = (
        "class Coordinate:\n"
        '    """Coordinate Data"""\n'
        "    COMPILED = True\n"
        "    PREFAB_FIELDS = ['x', 'y']\n"
        "    x: float\n"
        "    y: float\n"
        "\n"
        "    def __init__(self, x: float, y: float):\n"
        "        self.x = x\n"
        "        self.y = y\n"
        "\n"
        "    def __repr__(self):\n"
        "        return f'{type(self).__qualname__}(x={self.x!r}, y={self.y!r})'\n"
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
    ex_plain = Path(__file__).parent / "compile_targets" / "example_plain.py"
    result = preview(ex_plain, use_black=False)
    code = (
        "class Coordinate:\n"
        "    x: float\n"
        "    y: float\n"
        "\n"
        "    def __init__(self, x: float, y: float):\n"
        "        self.x = x\n"
        "        self.y = y\n"
        "\n"
        "    def __repr__(self):\n"
        "        return f'{type(self).__qualname__}(x={self.x!r}, y={self.y!r})'\n"
        "\n"
        "    def __eq__(self, other):\n"
        "        return (self.x, self.y) == (other.x, other.y) "
        "if self.__class__ == other.__class__ else NotImplemented"
    )

    assert result == code


def test_horriblemess():
    import textwrap
    source = textwrap.dedent("""
    @prefab(compile_prefab=True, repr=False, eq=False)
    class HorribleMess:
        # Nobody should write a class like this, but it should still work
        x: str
        x = attribute(default="fake_test", init=False)
        x: str = "test"  # This should override the init False statement
        y: str = "test_2"
        y: str
    """)

    code = textwrap.dedent("""
    class HorribleMess:
        COMPILED = True
        PREFAB_FIELDS = ['x', 'y']
        __match_args__ = ('x', 'y')
        x: str
        y: str
        
        def __init__(self, x: str='test', y: str='test_2'):
            self.x = x
            self.y = y
    """)

    result = rewrite_code(source)

    assert result.strip() == code.strip()