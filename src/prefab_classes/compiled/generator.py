import ast
from typing import Any, Optional, Union

from ..constants import (
    PRE_INIT_FUNC,
    POST_INIT_FUNC,
    PREFAB_INIT_FUNC,
    DECORATOR_NAME,
    ATTRIBUTE_FUNCNAME,
    FIELDS_ATTRIBUTE,
    COMPILED_FLAG,
    COMPILE_ARGUMENT,
    CLASSVAR_NAME,
)
from ..live import prefab, attribute
from ..exceptions import CompiledPrefabError

assignment_type = Union[ast.AnnAssign, ast.Assign]


# noinspection PyArgumentList
@prefab
class Field:
    name: str
    field: Any
    default: Any = None
    default_factory: ast.Name = None
    converter: ast.Name = None
    init_: bool = True
    repr_: bool = True
    kw_only: bool = False
    annotation: Any = None
    attribute_func: bool = False

    @property
    def default_factory_call(self):
        return ast.Call(func=self.default_factory, args=[], keywords=[])

    def converter_call(self, arg):
        return ast.Call(func=self.converter, args=[arg], keywords=[])

    def ast_attribute(
        self,
        obj_name="self",
        ctx: Union[type[ast.Load], type[ast.Store]] = ast.Load,
    ):
        """Get the ast.Attribute form for loading this attribute"""
        attrib = ast.Attribute(
            value=ast.Name(id=obj_name, ctx=ast.Load()),
            attr=self.name,
            ctx=ctx(),
        )
        return attrib

    @classmethod
    def from_keywords(cls, name, field, keywords, annotation=None):
        keys = {k.arg: k.value for k in keywords}
        default = keys.get("default", None)
        default_factory = keys.get("default_factory", None)
        converter = keys.get("converter", None)
        try:
            init_ = keys["init"].value
        except KeyError:
            init_ = True
        try:
            repr_ = keys["repr"].value
        except KeyError:
            repr_ = True
        try:
            kw_only = keys["kw_only"].value
        except KeyError:
            kw_only = False

        if not init_ and default is None and default_factory is None:
            raise CompiledPrefabError(
                "Must provide a default value/factory if the attribute is not in init."
            )

        if kw_only and not init_:
            raise CompiledPrefabError(
                "Attribute cannot be keyword only if it is not in init."
            )

        if default and default_factory:
            raise CompiledPrefabError(
                "Cannot define both a default value and a default factory."
            )

        return cls(
            name=name,
            field=field,
            default=default,
            default_factory=default_factory,
            converter=converter,
            init_=init_,
            repr_=repr_,
            kw_only=kw_only,
            annotation=annotation,
            attribute_func=True,
        )


# noinspection PyArgumentList,PyAttributeOutsideInit
@prefab
class PrefabDetails:
    name: str
    node: ast.ClassDef
    decorator: Any
    fields: dict[str, "Field"] = attribute(default_factory=dict)
    init: bool = True
    repr: bool = True
    eq: bool = True
    iter: bool = False
    match_args: bool = True
    compile_prefab: bool = False
    compile_plain: bool = False
    compile_fallback: bool = False
    compile_slots: bool = False
    parents: Optional[list[str]] = None

    def __prefab_post_init__(self):
        self._resolved_parents = False
        self._generated_fields = False
        self._generated_match_args = False
        self._generated_slots = False
        self._generated_init = False
        self._generated_repr = False
        self._generated_eq = False
        self._generated_iter = False
        self._method_visitor = None

    @property
    def field_names(self):
        return list(self.fields.keys())

    @property
    def field_list(self):
        return list(self.fields.values())

    @property
    def method_names(self):
        if not self._method_visitor:
            self._method_visitor = GatherFuncNames()
            self._method_visitor.visit(self.node)
        return self._method_visitor.methodnames

    @staticmethod
    def call_method(method_name, args=None, keywords=None):
        args = args if args else []
        keywords = keywords if keywords else []
        attrib = ast.Attribute(
            value=ast.Name(id="self", ctx=ast.Load()),
            attr=method_name,
            ctx=ast.Load(),
        )
        call = ast.Call(func=attrib, args=args, keywords=keywords)
        return ast.Expr(value=call)

    @property
    def pre_init_call(self):
        return self.call_method(PRE_INIT_FUNC)

    @property
    def post_init_call(self):
        return self.call_method(POST_INIT_FUNC)

    @property
    def ast_qualname_str(self):
        call = ast.Call(
            func=ast.Name(id='type', ctx=ast.Load()),
            args=[ast.Name(id='self', ctx=ast.Load())],
            keywords=[]
        )
        attrib = ast.Attribute(
            value=call,
            attr='__qualname__',
            ctx=ast.Load()
        )
        value = ast.FormattedValue(value=attrib, conversion=-1)
        return value

    def discover_fields(self):
        def funcid_or_none(value):
            """get .func.id or return None"""
            return getattr(getattr(value, "func", None), "id", None)

        fields: list["Field"] = []

        # If there are any plain assignments, annotated assignments that
        # do not use attribute() calls must be removed to match 'live'
        # behaviour.
        require_attribute_func = False

        for item in self.node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.annotation, ast.Name):
                    # Class ClassVar with no subscript
                    if CLASSVAR_NAME in item.annotation.id:
                        continue
                elif isinstance(item.annotation, ast.Constant):
                    # String 'ClassVar
                    if CLASSVAR_NAME in item.annotation.value:
                        continue
                elif isinstance(item.annotation, ast.Subscript):
                    # Subscripted classvar
                    v = item.annotation.value
                    if isinstance(v, ast.Name):
                        if CLASSVAR_NAME in v.id:
                            continue
                    elif isinstance(v, ast.Attribute):
                        if CLASSVAR_NAME in v.attr:
                            continue

                field_name = getattr(item.target, "id")
                # Case that the value is an attribute() call
                if funcid_or_none(item.value) == ATTRIBUTE_FUNCNAME:
                    field = Field.from_keywords(
                        name=field_name,
                        field=item,
                        keywords=item.value.keywords,
                        annotation=item.annotation,
                    )
                else:
                    field = Field(
                        name=field_name,
                        field=item,
                        default=item.value,
                        annotation=item.annotation,
                    )
                fields.append(field)
            elif (
                isinstance(item, ast.Assign)
                and len(item.targets) == 1
                and isinstance(item.value, ast.Call)
            ):
                field_name = getattr(item.targets[0], "id")
                field = Field.from_keywords(
                    name=field_name, field=item, keywords=item.value.keywords
                )
                fields.append(field)
                require_attribute_func = True

        # Clear fields that are generated just by annotations
        if require_attribute_func:
            fields = [field for field in fields if field.attribute_func]

        # Clear the fields from he self.node body
        for item in fields:
            self.node.body.remove(item.field)

        self.fields = {field.name: field for field in fields}

    def generate_slots(self):
        """Generate slots before looking at inheritance"""
        if self._generated_slots or not self.compile_slots:
            return

        slot_consts = [ast.Constant(value=name) for name in self.field_names]
        target = ast.Name(id="__slots__", ctx=ast.Store())
        assignment = ast.Assign(
            targets=[target], value=ast.Tuple(elts=slot_consts, ctx=ast.Load())
        )

        self.node.body.insert(0, assignment)  # Put slots first

    def discover_parents(self):
        if self.parents is None:
            self.parents = [getattr(item, "id") for item in self.node.bases]
        if self.name in self.parents:
            raise CompiledPrefabError(f"Class {self.name} cannot inherit from itself.")

    def resolve_field_inheritance(self, prefabs: dict[str, "PrefabDetails"]):
        """
        Work out the complete list of fields in the inheritance tree.

        :param prefabs: The full dict of prefabs
        :return:
        """

        if self._resolved_parents:
            return self.fields

        # Because this uses a python dict and dicts preserve
        # order this means if a subclass replaces a value
        # it will remain in its original place in the init function
        # but with the new default value (or with the default removed)
        new_fields: dict[str, "Field"] = {}
        for parent_name in reversed(self.parents):
            if parent_name not in prefabs:
                raise CompiledPrefabError(
                    f"Compiled prefabs can only inherit from other compiled prefabs in the same module.",
                    f"{self.name} attempted to inherit from {parent_name}",
                )
            parent_fields = prefabs[parent_name].resolve_field_inheritance(prefabs)
            new_fields.update(parent_fields)

        new_fields.update(self.fields)
        self.fields = new_fields

        self._resolved_parents = True

        return self.fields

    def generate_fields_attribute(self):
        if self._generated_fields:
            return  # Only generate once

        # Remove the decorator
        self.node.decorator_list.remove(self.decorator)
        if not self.compile_plain:
            compiled_flag = ast.Assign(
                targets=[ast.Name(id=COMPILED_FLAG, ctx=ast.Store())],
                value=ast.Constant(value=True),
            )
            self.node.body.insert(0, compiled_flag)

            field_consts = [ast.Constant(value=name) for name in self.field_names]
            target = ast.Name(id=FIELDS_ATTRIBUTE, ctx=ast.Store())
            assignment = ast.Assign(
                targets=[target],
                value=ast.List(elts=field_consts, ctx=ast.Load()),
            )

            self.node.body.insert(1, assignment)

        self._generated_fields = True

    def generate_match_args(self):
        if self._generated_match_args or not self.match_args:
            return

        field_consts = [ast.Constant(value=name) for name in self.field_names]
        target = ast.Name(id="__match_args__", ctx=ast.Store())
        assignment = ast.Assign(
            targets=[target],
            value=ast.Tuple(elts=field_consts, ctx=ast.Load()),
        )
        self.node.body.insert(0, assignment)

    def generate_init(self):
        if self._generated_init:
            return

        funcname = "__init__" if self.init else PREFAB_INIT_FUNC

        posonlyargs = []  # Unused
        args = []
        defaults = []
        kwonlyargs = []
        kw_defaults = []

        body = []

        if PRE_INIT_FUNC in self.method_names:
            body.append(self.pre_init_call)

        has_default = False

        args.append(ast.arg(arg="self"))

        for field in self.field_list:
            # if init is false, just assign the default value in the body
            if field.init_ is False:
                if field.default:
                    assignment_value = field.default
                else:
                    assignment_value = field.default_factory_call
            else:
                # Define the init signature
                assignment_value = ast.Name(id=field.name, ctx=ast.Load())
                if field.default or field.default_factory:
                    # Include the annotation if this is an annotated value
                    if hasattr(field, "annotation"):
                        arg = ast.arg(arg=field.name, annotation=field.annotation)
                    else:
                        arg = ast.arg(arg=field.name)

                    # For regular defaults, assign in the signature as expected
                    if field.default:
                        if field.kw_only:
                            kw_defaults.append(field.default)
                        else:
                            defaults.append(field.default)
                    # For factories, call the function in the body if the value is None
                    else:
                        if field.kw_only:
                            kw_defaults.append(ast.Constant(value=None))
                        else:
                            defaults.append(ast.Constant(value=None))

                        assignment_value = ast.IfExp(
                            test=ast.Compare(
                                left=ast.Name(id=field.name, ctx=ast.Load()),
                                ops=[ast.IsNot()],
                                comparators=[ast.Constant(value=None)],
                            ),
                            body=ast.Name(id=field.name, ctx=ast.Load()),
                            orelse=field.default_factory_call,
                        )
                    if field.kw_only:
                        kwonlyargs.append(arg)
                    else:
                        # Declare that there's a parameter with default value
                        # in order to fail if there's one declared afterwards
                        has_default = True
                        args.append(arg)

                # Simpler code for values with no defaults
                else:
                    if has_default and not field.kw_only:
                        raise SyntaxError(
                            "non-default argument follows default argument"
                        )
                    if field.annotation:
                        arg = ast.arg(arg=field.name, annotation=field.annotation)
                    else:
                        arg = ast.arg(arg=field.name)

                    if field.kw_only:
                        kw_defaults.append(None)
                        kwonlyargs.append(arg)
                    else:
                        args.append(arg)

            # Define the body
            body.append(
                ast.Assign(
                    targets=[field.ast_attribute(ctx=ast.Store)],
                    value=field.converter_call(assignment_value)
                    if field.converter
                    else assignment_value,
                )
            )

        if not self.field_list:
            body.append(ast.Pass())

        if POST_INIT_FUNC in self.method_names:
            body.append(self.post_init_call)

        arguments = ast.arguments(
            posonlyargs=posonlyargs,
            args=args,
            kwonlyargs=kwonlyargs,
            kw_defaults=kw_defaults,
            defaults=defaults,
        )

        init_func = ast.FunctionDef(
            name=funcname,
            args=arguments,
            body=body,
            decorator_list=[],
            returns=None,
        )

        self.node.body.append(init_func)
        self._generated_init = True

    def generate_repr(self):
        if self._generated_repr or not self.repr:
            return

        arguments = [ast.arg(arg="self")]
        args = ast.arguments(
            posonlyargs=[],
            args=arguments,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )

        field_strings = [
            self.ast_qualname_str,
            ast.Constant(value="(")
        ]
        for i, field in enumerate(self.field_list):
            if i > 0:
                field_strings.append(ast.Constant(value=", "))
            target = ast.Constant(value=f"{field.name}=")
            value = ast.FormattedValue(
                value=field.ast_attribute(),
                conversion=114,  # REPR formatting
            )
            field_strings.extend([target, value])

        field_strings.append(ast.Constant(value=")"))

        repr_string = ast.JoinedStr(values=field_strings)
        body = [ast.Return(value=repr_string)]

        repr_func = ast.FunctionDef(
            name="__repr__",
            args=args,
            body=body,
            decorator_list=[],
            returns=None,
        )

        self.node.body.append(repr_func)
        self._generated_repr = True

    def generate_eq(self):
        if self._generated_eq or not self.eq:
            return

        arguments = [ast.arg(arg="self"), ast.arg(arg="other")]

        if self.field_list:
            # elt = element I guess - but this is the terminology used in the
            # tuple AST function so elt it is.
            class_elts = []
            other_elts = []

            for field in self.field_list:
                for obj_name, elt_list in [
                    ("self", class_elts),
                    ("other", other_elts),
                ]:
                    elt_list.append(field.ast_attribute(obj_name))

            class_tuple = ast.Tuple(elts=class_elts, ctx=ast.Load())
            other_tuple = ast.Tuple(elts=other_elts, ctx=ast.Load())

            # (self.x, self.y, ...) == (other.x, other.y, ...)
            eq_comparison = ast.Compare(
                left=class_tuple, ops=[ast.Eq()], comparators=[other_tuple]
            )

        else:
            eq_comparison = ast.Constant(value="True")

        # (self.x, ...) == (other.x, ...) if self.__class__ == other.__class__ else NotImplemented
        left_ifexp = ast.Attribute(
            value=ast.Name(id="self", ctx=ast.Load()),
            attr="__class__",
            ctx=ast.Load(),
        )
        right_ifexp = ast.Attribute(
            value=ast.Name(id="other", ctx=ast.Load()),
            attr="__class__",
            ctx=ast.Load(),
        )

        class_expr = ast.IfExp(
            test=ast.Compare(
                left=left_ifexp, ops=[ast.Eq()], comparators=[right_ifexp]
            ),
            body=eq_comparison,
            orelse=ast.Name(id="NotImplemented", ctx=ast.Load()),
        )

        args = ast.arguments(
            posonlyargs=[],
            args=arguments,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )

        body = [ast.Return(value=class_expr)]

        eq_func = ast.FunctionDef(
            name="__eq__", args=args, body=body, decorator_list=[], returns=None
        )
        self.node.body.append(eq_func)
        self._generated_eq = True

    def generate_iter(self):
        if self._generated_iter or not self.iter:
            return

        arguments = [ast.arg(arg="self")]
        if self.field_list:
            body = [
                ast.Expr(value=ast.Yield(value=field.ast_attribute()))
                for field in self.field_list
            ]
        else:
            body = [
                ast.Expr(value=ast.YieldFrom(value=ast.Tuple(elts=[], ctx=ast.Load())))
            ]

        args = ast.arguments(
            posonlyargs=[],
            args=arguments,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )

        iter_func = ast.FunctionDef(
            name="__iter__",
            args=args,
            body=body,
            decorator_list=[],
            returns=None,
        )

        self.node.body.append(iter_func)
        self._generated_iter = True

    def generate_ast(self, prefabs: dict[str, "PrefabDetails"]):
        # Discover required details
        self.discover_fields()

        # Write slot AST independent of parent details
        self.generate_slots()  # Slots should only be defined by the current class

        self.discover_parents()
        self.resolve_field_inheritance(prefabs)

        # Rewrite AST
        self.generate_fields_attribute()
        self.generate_match_args()
        self.generate_init()
        self.generate_repr()
        self.generate_eq()
        self.generate_iter()


class GatherFuncNames(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.methodnames = set()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.methodnames.add(node.name)


class GatherPrefabs(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.prefabs: dict[str, PrefabDetails] = {}

    def visit_ClassDef(self, node: ast.ClassDef):
        # Looking for a call to DECORATOR_NAME with COMPILE_ARGUMENT == True
        # Check for plain classes, these will have the decorator removed and no fields defined
        prefab_decorator = None
        for item in node.decorator_list:
            if (
                isinstance(item, ast.Call)
                and getattr(item.func, "id") == DECORATOR_NAME
            ):
                for keyword in item.keywords:
                    if (
                        keyword.arg == COMPILE_ARGUMENT
                        and getattr(keyword.value, "value") is True
                    ):
                        prefab_decorator = item
                        break
            if prefab_decorator:
                break

        if prefab_decorator:
            keywords = {
                kw.arg: getattr(kw.value, "value") for kw in prefab_decorator.keywords
            }
            prefab_details = PrefabDetails(
                name=node.name,
                node=node,
                decorator=prefab_decorator,
                **keywords,
            )

            self.prefabs[prefab_details.name] = prefab_details


def compile_prefabs(source: str) -> ast.Module:
    """
    Generate the AST tree with the modified code for prefab classes

    :param source:
    :return:
    """
    tree = ast.parse(source)
    gatherer = GatherPrefabs()
    gatherer.visit(tree)

    prefabs = gatherer.prefabs

    # First gather field lists and parent class names
    for p in prefabs.values():
        p.generate_ast(prefabs)

    ast.fix_missing_locations(tree)

    return tree
