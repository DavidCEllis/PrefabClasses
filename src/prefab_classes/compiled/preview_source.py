import ast
import os


def preview_source(source: str, use_black: bool = True):
    from .generator import compile_prefabs

    tree = compile_prefabs(source)
    # Black usage is not covered in case black changes formatting.
    if use_black:  # pragma: no cover
        try:
            import black

            return black.format_str(ast.unparse(tree), mode=black.Mode())
        except ImportError:
            return ast.unparse(tree)
    else:
        return ast.unparse(tree)


def preview(pth: os.PathLike, use_black: bool = True):
    """
    Preview the result of running the generator on a python file
    This is mainly here for debugging and testing but can also be useful
    if users are unsure how the class will be generated.

    :param pth: Path to the .py
    :param use_black: use the black formatter to make the result easier to read
                      if black is installed.
    :return: string output of generated python code from the AST
    """
    with open(pth, mode="r", encoding="utf-8") as f:
        source = f.read()

    return preview_source(source, use_black=use_black)
