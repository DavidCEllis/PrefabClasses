import ast
from pathlib import Path


def preview(pth: Path, use_black=True):
    """
    Preview the result of running the generator on a python file
    This is mainly here for debugging and testing but can also be useful
    if users are unsure how the class will be generated.

    :param pth: Path to the .py
    :param use_black: use the black formatter to make the result easier to read
                      if black is installed.
    :return: string output of generated python code from the AST
    """
    from .generator import compile_prefabs

    source = pth.read_text()
    tree = compile_prefabs(source)
    if use_black:
        try:
            import black

            return black.format_str(ast.unparse(tree), mode=black.Mode())
        except ImportError:
            return ast.unparse(tree)
    else:
        return ast.unparse(tree)
