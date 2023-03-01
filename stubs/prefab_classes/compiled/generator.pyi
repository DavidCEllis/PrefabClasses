import ast
from ..constants import (
    ATTRIBUTE_FUNCNAME as ATTRIBUTE_FUNCNAME,
    CLASSVAR_NAME as CLASSVAR_NAME,
    COMPILED_FLAG as COMPILED_FLAG,
    COMPILE_ARGUMENT as COMPILE_ARGUMENT,
    DECORATOR_NAME as DECORATOR_NAME,
    FIELDS_ATTRIBUTE as FIELDS_ATTRIBUTE,
    POST_INIT_FUNC as POST_INIT_FUNC,
    PREFAB_INIT_FUNC as PREFAB_INIT_FUNC,
    PRE_INIT_FUNC as PRE_INIT_FUNC,
)
from ..dynamic import prefab as prefab
from ..exceptions import CompiledPrefabError as CompiledPrefabError
from _typeshed import Incomplete
from functools import cached_property
from typing import Union

assignment_type: str
prefab_essentials: set[str]

class Field:
    name: str
    field: Union[ast.AnnAssign, ast.Assign]
    default: Union[None, ast.expr]
    default_factory: Union[None, ast.expr]
    init_: bool
    repr_: bool
    kw_only: bool
    exclude_field: bool
    annotation: Union[None, ast.expr]
    attribute_func: bool
    def __prefab_post_init__(self) -> None: ...

    @cached_property
    def default_factory_call(self) -> ast.Call: ...

    def ast_attribute(
        self, obj_name: str = ..., ctx: Union[type[ast.Load], type[ast.Store]] = ...
    ): ...
    @classmethod
    def from_keywords(
        cls, name, field, keywords, annotation: Incomplete | None = ...
    ): ...

class PrefabDetails:
    name: str
    node: ast.ClassDef
    decorator: ast.Call
    init: bool
    repr: bool
    eq: bool
    iter: bool
    match_args: bool
    kw_only: bool
    frozen: bool
    compile_prefab: bool
    compile_plain: bool
    compile_fallback: bool
    compile_slots: bool

    def __prefab_post_init__(self) -> None: ...

    @property
    def field_names(self): ...

    @property
    def field_list(self): ...

    @property
    def resolved_field_names(self): ...

    @property
    def resolved_field_list(self): ...

    def gather_methods_arguments(self) -> None: ...

    @property
    def defined_attr_names(self): ...

    @property
    def func_arguments(self): ...

    @property
    def resolved_func_arguments(self) -> dict[str, list[str]]: ...

    @staticmethod
    def call_method(
        method_name, *, args: Incomplete | None = ..., keywords: Incomplete | None = ...
    ): ...

    @property
    def pre_init_call(self): ...

    @property
    def post_init_call(self): ...

    @property
    def ast_qualname_str(self): ...

    @cached_property
    def fields(self) -> dict[str, Field]: ...

    @cached_property
    def parents(self) -> list[str]: ...

    def resolve_inheritance(self, prefabs: dict[str, "PrefabDetails"]): ...

    @property
    def resolved_fields(self) -> dict[str, Field]: ...

    @cached_property
    def compile_flag(self) -> ast.Assign: ...

    @property
    def fields_assignment(self) -> ast.Assign: ...

    @property
    def internals_assignment(self) -> ast.Assign: ...

    @property
    def slots_assignment(self) -> ast.Assign: ...

    @property
    def match_args_assignment(self) -> ast.Assign: ...

    @property
    def init_method(self) -> ast.FunctionDef: ...

    @property
    def repr_method(self) -> ast.FunctionDef: ...

    @property
    def eq_method(self) -> ast.FunctionDef: ...

    @property
    def iter_method(self) -> ast.FunctionDef: ...

    @property
    def frozen_exception_import(self) -> ast.ImportFrom: ...

    @property
    def frozen_setattr_method(self) -> ast.FunctionDef: ...

    @property
    def frozen_delattr_method(self) -> ast.FunctionDef: ...

    def generate_ast(self, prefabs: dict[str, "PrefabDetails"]) -> None: ...

class GatherClassAttrs(ast.NodeVisitor):
    attrnames: Incomplete
    func_arguments: Incomplete
    def __init__(self) -> None: ...
    def visit_FunctionDef(self, node: ast.FunctionDef): ...
    def visit_Assign(self, node: ast.Assign): ...
    def visit_AnnAssign(self, node: ast.AnnAssign): ...

class GatherPrefabs(ast.NodeVisitor):
    prefabs: Incomplete
    dynamic_prefabs_present: bool
    import_statements: Incomplete
    def __init__(self) -> None: ...
    def visit_ClassDef(self, node: ast.ClassDef) -> None: ...
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None: ...

def compile_prefabs(source: str) -> ast.Module: ...
