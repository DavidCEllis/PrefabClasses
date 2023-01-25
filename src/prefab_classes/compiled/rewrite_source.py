from ..exceptions import CompiledPrefabError


COMPILE_COMMENT = """
# DO NOT MANUALLY EDIT THIS FILE
# MODULE: {dest}
# GENERATED FROM: {source}
# USING prefab_classes VERSION: {version}
""".strip()


def rewrite_code(source: str, *, use_black: bool = False):
    import ast
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
    header_comment: str = COMPILE_COMMENT,
    use_black: bool = False,
):
    """
    Parse a source python file and rewrite any @prefab(compile_prefab=True) decorated
    classes. Unparse the output back to a new source file.

    As the compiled method uses the AST to handle parsing any comments and formatting
    will be stripped from the resulting code.

    Currently an option to use Black to reformat the code to make it slightly more
    readable is provided. Potentially this could be extended to be more generic.

    :param source_path: Source file to rewrite
    :param dest_path: Destination output for compiled prefab code
    :param header_comment: String to insert at the top of the file
    :param use_black: Attempt to run black on the output to make it more readable
    """
    from .. import __version__
    from pathlib import Path

    source_path, dest_path = Path(source_path), Path(dest_path)

    if source_path == dest_path:
        raise CompiledPrefabError("Can not overwrite source file.")

    source = source_path.read_text(encoding="utf-8")

    compiled_source = rewrite_code(source, use_black=use_black)

    with open(dest_path, mode="w", encoding="utf-8") as f:
        f.write(
            header_comment.format(
                dest=dest_path.name, source=source_path.name, version=__version__
            )
        )
        f.write("\n\n")
        f.write(compiled_source)


def get_sources_to_compare(
    source_path,
    dest_path,
    *,
    header_comment: str = COMPILE_COMMENT,
    use_black: bool = False,
) -> tuple[str, str]:
    """
    Get the converted original source and the dest source.

    Currently an option to use Black to reformat the code to make it slightly more
    readable is provided. Potentially this could be extended to be more generic.

    :param source_path: Source file to rewrite
    :param dest_path: Destination output for compiled prefab code
    :param header_comment: String to insert at the top of the file
    :param use_black: Attempt to run black on the output to make it more readable
    """
    from .. import __version__
    from pathlib import Path
    from io import StringIO

    source_path, dest_path = Path(source_path), Path(dest_path)

    if source_path == dest_path:
        raise CompiledPrefabError("Can not overwrite source file.")

    source = source_path.read_text(encoding="utf-8")

    compiled_source = rewrite_code(source, use_black=use_black)

    dest_source = dest_path.read_text()

    str_out = StringIO()

    str_out.write(
        header_comment.format(
            dest=dest_path.name, source=source_path.name, version=__version__
        )
    )
    str_out.write("\n\n")
    str_out.write(compiled_source)

    return str_out.getvalue(), dest_source
