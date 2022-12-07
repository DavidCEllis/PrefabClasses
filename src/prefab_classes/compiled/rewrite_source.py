import ast

from ..exceptions import CompiledPrefabError


COMPILE_COMMENT = """
# DO NOT MANUALLY EDIT THIS FILE
# MODULE: {dest}
# GENERATED FROM: {source}
# USING prefab_classes VERSION: {version}
""".strip()


def rewrite_code(source: str, *, use_black: bool = False):
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


def preview(pth, *, use_black: bool = True):
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

    return rewrite_code(source, use_black=use_black)


def rewrite_to_py(
        source_path,
        dest_path,
        *,
        header_comment=COMPILE_COMMENT,
        use_black=False,
        delete_firstlines=0
):
    from .. import __version__
    from pathlib import Path

    source_path, dest_path = Path(source_path), Path(dest_path)

    if source_path == dest_path:
        raise CompiledPrefabError("Can not overwrite source file.")

    source = source_path.read_text(encoding="utf-8")

    compiled_source = rewrite_code(source, use_black=use_black)
    if delete_firstlines > 0:
        compiled_lines = compiled_source.split('\n')
        compiled_source = '\n'.join(compiled_lines[delete_firstlines:])

    with open(dest_path, mode='w', encoding='utf-8') as f:
        f.write(header_comment.format(dest=dest_path.name, source=source_path.name, version=__version__))
        f.write('\n\n')
        f.write(compiled_source)