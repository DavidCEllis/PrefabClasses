import ast
from functools import cached_property
from collections import defaultdict

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
    INTERNAL_DICT,
)
from ..dynamic import prefab, attribute
from ..exceptions import CompiledPrefabError

assignment_type = "ast.AnnAssign | ast.Assign"
prefab_essentials = {DECORATOR_NAME, ATTRIBUTE_FUNCNAME}


def _is_classvar(item):
    if isinstance(item.annotation, ast.Name):
        # Class ClassVar with no subscript
        if CLASSVAR_NAME in item.annotation.id:
            return True
    elif isinstance(item.annotation, ast.Constant):
        # String 'ClassVar'
        if CLASSVAR_NAME in item.annotation.value:
            return True
    elif isinstance(item.annotation, ast.Subscript):
        # Subscripted classvar
        v = item.annotation.value
        if isinstance(v, ast.Name):
            if CLASSVAR_NAME in v.id:
                return True
        elif isinstance(v, ast.Attribute):
            if CLASSVAR_NAME in v.attr:
                return True


def _is_kw_only_sentinel(item):
    if isinstance(item.annotation, ast.Name):
        # Class KW_ONLY
        if "KW_ONLY" in item.annotation.id:
            return True
    elif isinstance(item.annotation, ast.Constant):
        # String 'KW_ONLY'
        if "KW_ONLY" in item.annotation.value:
            return True


# noinspection PyArgumentList
@prefab
class Field:
    name: str = attribute()
    field: assignment_type = attribute()
    default: None | ast.expr = attribute(default=None)
    default_factory: None | ast.expr = attribute(default=None)
    init_: bool = attribute(default=True)
    repr_: bool = attribute(default=True)
    compare: bool = attribute(default=True)
    kw_only: bool = attribute(default=False)
    exclude_field: bool = attribute(default=False)
    annotation: None | ast.expr = attribute(default=None)
    attribute_func: bool = attribute(default=False)

    # Indicator that this Field should be made KW_ONLY
    _kw_only_flagged = attribute(default=False, init=False, repr=False)

    # This keeps a history of all assignments that have been used to remove
    # them from the AST after compilation
    all_assignments: set[assignment_type] = attribute(default_factory=set, init=False, repr=False)

    def __prefab_post_init__(self):
        self.all_assignments.add(self.field)

    @cached_property
    def default_factory_call(self):
        return ast.Call(func=self.default_factory, args=[], keywords=[])

    def ast_attribute(
        self,
        obj_name="self",
        ctx: type[ast.Load] | type[ast.Store] = ast.Load,
    ):
        """Get the ast.Attribute form for loading this attribute"""
        attrib = ast.Attribute(
            value=ast.Name(id=obj_name, ctx=ast.Load()),
            attr=self.name,
            ctx=ctx(),
        )
        return attrib

    @property
    def ast_annassign(self):
        """
        Get an annotated assignment with no value for this field or return None
        """
        if self.annotation:
            name = ast.Name(id=self.name, ctx=ast.Store())
            assign = ast.AnnAssign(target=name, annotation=self.annotation, value=None, simple=True)
            return assign
        return None

    @classmethod
    def from_keywords(cls, name, field, keywords, annotation=None):
        keys = {k.arg: k.value for k in keywords}
        default = keys.get("default", None)
        default_factory = keys.get("default_factory", None)
        try:
            init_ = keys["init"].value
        except KeyError:
            init_ = True
        try:
            repr_ = keys["repr"].value
        except KeyError:
            repr_ = True
        try:
            compare = keys["compare"].value
        except KeyError:
            compare = True
        try:
            kw_only = keys["kw_only"].value
        except KeyError:
            kw_only = False
        try:
            exclude_field = keys["exclude_field"].value
        except KeyError:
            exclude_field = False

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
            init_=init_,
            repr_=repr_,
            compare=compare,
            kw_only=kw_only,
            exclude_field=exclude_field,
            annotation=annotation,
            attribute_func=True,
        )


# noinspection PyProtectedMember
@prefab
class PrefabDetails:
    name: str = attribute()
    node: ast.ClassDef = attribute()
    decorator: ast.Call = attribute()
    init: bool = attribute(default=True)
    repr: bool = attribute(default=True)
    eq: bool = attribute(default=True)
    iter: bool = attribute(default=False)
    match_args: bool = attribute(default=True)
    kw_only: bool = attribute(default=False)
    frozen: bool = attribute(default=False)
    compile_prefab: bool = attribute(default=False)
    compile_plain: bool = attribute(default=False)
    compile_fallback: bool = attribute(default=False)
    compile_slots: bool = attribute(default=False)

    # Private internal variables
    _resolved_fields: None | dict[str, Field] = attribute(
        default=None, init=False, repr=False, compare=False
    )
    _prefab_map: None | dict[str, 'PrefabDetails'] = attribute(
        default=None, init=False, repr=False, compare=False
    )
    _flag_kw_only: None | ast.AnnAssign = attribute(
        default=None, init=False, repr=False, compare=False
    )
    _defined_attr_names: None | set[str] = attribute(
        default=None, init=False, repr=False, compare=False
    )
    _func_arguments: None | dict[str, dict[str, None | ast.Expr]] = attribute(
        default=None, init=False, repr=False, compare=False
    )
    _resolved_func_arguments: None | dict[str, dict[str, None | ast.Expr]] = attribute(
        default=None, init=False, repr=False, compare=False
    )

    @property
    def field_names(self):
        return list(self.fields.keys())

    @property
    def field_list(self):
        return list(self.fields.values())

    @property
    def resolved_field_names(self):
        # Field names including inherited fields
        return list(self._resolved_fields.keys())

    @property
    def resolved_field_list(self):
        # Field values including inherited fields
        return list(self._resolved_fields.values())

    def gather_methods_arguments(self):
        method_visitor = GatherClassAttrs()
        method_visitor.visit(self.node)
        self._defined_attr_names = method_visitor.attrnames
        self._func_arguments = method_visitor.func_arguments

    @property
    def defined_attr_names(self):
        """
        Get existing assigned names
        """
        if self._defined_attr_names is None:
            self.gather_methods_arguments()
        return self._defined_attr_names

    @property
    def func_arguments(self):
        if self._func_arguments is None:
            self.gather_methods_arguments()
        return self._func_arguments

    @property
    def resolved_func_arguments(self):
        if self._resolved_func_arguments is None:
            raise CompiledPrefabError(
                "Inheritance has not yet been resolved, "
                "call resolve_inheritance first"
            )
        return self._resolved_func_arguments

    @staticmethod
    def call_method(method_name, *, args=None, keywords=None):
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
        pre_init_args = self.resolved_func_arguments[PRE_INIT_FUNC].keys()
        call_args = [
            ast.keyword(arg=attrib, value=ast.Name(id=attrib, ctx=ast.Load()))
            for attrib in pre_init_args
            if attrib != "self"
        ]

        return self.call_method(PRE_INIT_FUNC, keywords=call_args)

    @property
    def post_init_call(self):
        post_init_args = self.resolved_func_arguments[POST_INIT_FUNC].keys()
        call_args = [
            ast.keyword(arg=attrib, value=ast.Name(id=attrib, ctx=ast.Load()))
            for attrib in post_init_args
            if attrib != "self"
        ]
        return self.call_method(POST_INIT_FUNC, keywords=call_args)

    @property
    def ast_qualname_str(self):
        call = ast.Call(
            func=ast.Name(id="type", ctx=ast.Load()),
            args=[ast.Name(id="self", ctx=ast.Load())],
            keywords=[],
        )
        attrib = ast.Attribute(value=call, attr="__qualname__", ctx=ast.Load())
        value = ast.FormattedValue(value=attrib, conversion=-1)
        return value

    @cached_property
    def fields(self) -> dict[str, Field]:
        def funcid_or_none(value):
            """get .func.id or return None"""
            return getattr(getattr(value, "func", None), "id", None)

        fields: dict[str, Field] = {}

        # This stores potential default values
        # Given as plain assignments that are later typed
        # Keep the assignments to be cleared later
        potential_defaults: dict = {}
        plain_assignments: dict[set[assignment_type]] = defaultdict(set)

        flag_kw_only = False
        for item in self.node.body:
            if isinstance(item, ast.AnnAssign):
                # Test if something is a classvar
                if _is_classvar(item):
                    continue
                elif _is_kw_only_sentinel(item):
                    flag_kw_only = True
                    self._flag_kw_only = (
                        item  # Store the item itself to be removed later
                    )
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

                    # Get any potential assignments to clear after generation
                    old_field = fields.get(field_name, None)
                    if old_field:
                        field.all_assignments.update(old_field.all_assignments)
                    else:
                        field.all_assignments.update(plain_assignments[field_name])

                else:
                    if field_name in fields and item.value is None:
                        # If the field exists and this is just an annotation
                        # Update the field annotation
                        field = fields[field_name]
                        field.annotation = item.annotation
                        field.all_assignments.add(item)
                    else:
                        # Otherwise make a new field
                        field = Field(
                            name=field_name,
                            field=item,
                            default=item.value,
                            annotation=item.annotation,
                        )

                        old_field = fields.get(field_name, None)
                        if old_field:
                            field.all_assignments.update(old_field.all_assignments)
                        elif field.default is None:
                            field.default = potential_defaults.get(field_name, None)
                            field.all_assignments.update(plain_assignments[field_name])

                if self.kw_only:
                    field.kw_only = True
                elif flag_kw_only:
                    # As KW_ONLY is ignored if plain assignments are used
                    # Just flag the field to be made KW_ONLY later if no
                    # plain assignments are used
                    field._kw_only_flagged = True

                fields[field_name] = field

            elif (
                isinstance(item, ast.Assign)
                and len(item.targets) == 1
            ):
                field_name = getattr(item.targets[0], "id")

                if (
                        isinstance(item.value, ast.Call)
                        and funcid_or_none(item.value) == ATTRIBUTE_FUNCNAME
                ):
                    # This is an attribute declaration
                    field = Field.from_keywords(
                        name=field_name, field=item, keywords=item.value.keywords
                    )
                    if self.kw_only:
                        field.kw_only = True

                    # If there is an old field copy the annotation and all assignment list over
                    old_field = fields.get(field_name, None)
                    if old_field:
                        field.annotation = old_field.annotation
                        field.all_assignments.update(old_field.all_assignments)
                    else:
                        # Otherwise copy potential plain assignments over
                        field.all_assignments.update(plain_assignments[field_name])

                    fields[field_name] = field
                else:
                    # This is a plain value
                    old_field = fields.get(field_name, None)
                    if old_field:
                        # Update the default value and add to the list of all fields
                        old_field.default = item.value
                        old_field.all_assignments.add(item)
                    else:
                        # Store the non-annotated values in case they
                        # subsequently get annotated
                        potential_defaults[field_name] = item.value
                        plain_assignments[field_name].add(item)

        # If there are any plain assignments, annotated assignments that
        # do not use attribute() calls must be removed to match 'dynamic'
        # behaviour. KW_ONLY should only be used if all assignments are annotated.
        require_attribute_func = any(v.annotation is None for v in fields.values())
        if require_attribute_func:
            fields = {k: v for k, v in fields.items() if v.attribute_func}
        else:
            # Make relevant fields kw_only if no plain assignments used
            for field in fields.values():
                if field._kw_only_flagged:
                    field.kw_only = True

        return fields

    @cached_property
    def parents(self) -> list[str]:
        parents = [
            getattr(item, "id")
            for item in self.node.bases
            if getattr(item, "id") != "object"  # Ignore inheritance from object
        ]
        if self.name in parents:
            raise CompiledPrefabError(f"Class {self.name} cannot inherit from itself.")
        return parents

    def resolve_inheritance(self, prefabs: dict[str, "PrefabDetails"]):
        """
        Work out the complete list of fields in the inheritance tree and the correct
        arguments for any pre_init or post_init functions.

        :param prefabs: The full dict of prefabs
        :return:
        """

        if prefabs == self._prefab_map:
            return

        self._prefab_map = prefabs

        # Because this uses a python dict and dicts preserve
        # order this means if a subclass replaces a value
        # it will remain in its original place in the init function
        # but with the new default value (or with the default removed)
        new_fields: dict[str, Field] = {}
        func_arguments: dict[str, dict[str, "None | ast.Expr"]] = {}
        for parent_name in reversed(self.parents):
            if parent_name not in prefabs:
                raise CompiledPrefabError(
                    f"Compiled prefabs can only inherit from other compiled prefabs in the same module.",
                    f"{self.name} attempted to inherit from {parent_name}",
                )
            prefabs[parent_name].resolve_inheritance(prefabs)
            new_fields.update(prefabs[parent_name].resolved_fields)
            func_arguments.update(prefabs[parent_name].resolved_func_arguments)

        new_fields.update(self.fields)
        func_arguments.update(self.func_arguments)

        self._resolved_fields = new_fields
        self._resolved_func_arguments = func_arguments

    @property
    def resolved_fields(self) -> dict[str, Field]:
        if self._resolved_fields is None:
            raise CompiledPrefabError(
                "Inheritance has not yet been resolved, "
                "call resolve_inheritance first"
            )
        return self._resolved_fields

    @property
    def compile_flag(self) -> ast.Assign:
        compiled_flag = ast.Assign(
            targets=[ast.Name(id=COMPILED_FLAG, ctx=ast.Store())],
            value=ast.Constant(value=True),
        )
        return compiled_flag

    @property
    def fields_assignment(self) -> ast.Assign:
        field_consts = [
            ast.Constant(value=field.name)
            for field in self.resolved_field_list
            if not field.exclude_field
        ]
        target = ast.Name(id=FIELDS_ATTRIBUTE, ctx=ast.Store())
        assignment = ast.Assign(
            targets=[target],
            value=ast.List(elts=field_consts, ctx=ast.Load()),
        )
        return assignment

    @property
    def internals_assignment(self) -> ast.Assign:
        return ast.Assign(
            targets=[ast.Name(id=INTERNAL_DICT, ctx=ast.Store())],
            value=ast.Dict(keys=[], values=[]),
        )

    @property
    def slots_assignment(self) -> ast.Assign:
        """Generate slots"""
        # Don't use resolved fields as we only want fields new to this class
        slot_consts = [ast.Constant(value=name) for name in self.field_names]
        target = ast.Name(id="__slots__", ctx=ast.Store())
        assignment = ast.Assign(
            targets=[target], value=ast.Tuple(elts=slot_consts, ctx=ast.Load())
        )

        return assignment

    @property
    def match_args_assignment(self) -> ast.Assign:
        field_consts = [
            ast.Constant(value=field.name)
            for field in self.resolved_field_list
            if not field.exclude_field
        ]
        target = ast.Name(id="__match_args__", ctx=ast.Store())
        assignment = ast.Assign(
            targets=[target],
            value=ast.Tuple(elts=field_consts, ctx=ast.Load()),
        )
        return assignment

    @property
    def init_method(self) -> ast.FunctionDef:
        funcname = "__init__" if self.init else PREFAB_INIT_FUNC

        posonlyargs = []  # Unused
        args = []
        defaults = []
        kwonlyargs = []
        kw_defaults = []

        body = []

        if PRE_INIT_FUNC in self.resolved_func_arguments:
            body.append(self.pre_init_call)

        # Get post_init_args
        post_init_args = self.resolved_func_arguments.get(POST_INIT_FUNC, {})

        has_default = False

        args.append(ast.arg(arg="self"))

        # If the __init__ body is empty we need a pass statement
        # Fields with init=False and no default don't exist in the __init__ function
        # So need to be excluded when checking for emptiness
        non_assigned_fields = 0

        for field in self.resolved_field_list:
            # if init is false, just assign the default value in the body
            if field.init_ is False:
                if field.default:
                    assignment_value = field.default
                elif field.default_factory:
                    assignment_value = field.default_factory_call
                else:
                    # Do not assign if no default is given.
                    assignment_value = None
            else:
                # Define the init signature
                assignment_value = ast.Name(id=field.name, ctx=ast.Load())
                if field.default or field.default_factory:

                    # If the argument is given to post_init with a different annotation
                    # Copy that annotation to __init__
                    post_annotation = post_init_args.get(field.name, None)

                    arg = ast.arg(
                        arg=field.name,
                        annotation=post_annotation if post_annotation else field.annotation
                    )

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

                    # If the argument is given to post_init with a different annotation
                    # Copy that annotation to __init__
                    post_annotation = post_init_args.get(field.name, None)

                    arg = ast.arg(
                        arg=field.name,
                        annotation=post_annotation if post_annotation else field.annotation
                    )

                    if field.kw_only:
                        kw_defaults.append(None)
                        kwonlyargs.append(arg)
                    else:
                        args.append(arg)

            if field.name not in post_init_args and field.exclude_field:
                raise CompiledPrefabError(
                    f"{field.name} is an excluded attribute but is not passed to post_init"
                )

            if field.name in post_init_args:
                # Factories should still run
                if field.default_factory:
                    body.append(
                        ast.Assign(
                            targets=[ast.Name(id=field.name, ctx=ast.Store())],
                            value=assignment_value,
                        )
                    )
            elif assignment_value is not None:
                body.append(
                    ast.Assign(
                        targets=[field.ast_attribute(ctx=ast.Store)],
                        value=assignment_value,
                    )
                )
            else:  # init=False and no default
                non_assigned_fields += 1

        if non_assigned_fields >= len(self.resolved_field_list):
            body.append(ast.Pass())

        if POST_INIT_FUNC in self.resolved_func_arguments:
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

        return init_func

    @property
    def repr_method(self) -> ast.FunctionDef:
        arguments = [ast.arg(arg="self")]
        args = ast.arguments(
            posonlyargs=[],
            args=arguments,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )

        field_strings = []
        use_eval_repr = True
        first_field = True
        for field in self.resolved_field_list:
            if use_eval_repr and (field.exclude_field or (field.repr_ ^ field.init_)):
                use_eval_repr = False

            if field.repr_ and not field.exclude_field:
                if first_field:
                    first_field = False
                else:
                    field_strings.append(ast.Constant(value=", "))
                target = ast.Constant(value=f"{field.name}=")
                value = ast.FormattedValue(
                    value=field.ast_attribute(),
                    conversion=114,  # REPR formatting
                )
                field_strings.extend([target, value])

        if use_eval_repr:
            field_strings = [
                self.ast_qualname_str,
                ast.Constant(value="("),
                *field_strings,
                ast.Constant(value=")"),
            ]
        else:
            if field_strings:
                field_strings = [
                    ast.Constant(value="<prefab "),
                    self.ast_qualname_str,
                    ast.Constant(value="; "),
                    *field_strings,
                    ast.Constant(value=">"),
                ]
            else:
                field_strings = [
                    ast.Constant(value="<prefab "),
                    self.ast_qualname_str,
                    ast.Constant(value=">"),
                ]

        repr_string = ast.JoinedStr(values=field_strings)
        body = [ast.Return(value=repr_string)]

        repr_func = ast.FunctionDef(
            name="__repr__",
            args=args,
            body=body,
            decorator_list=[],
            returns=None,
        )

        return repr_func

    @property
    def eq_method(self) -> ast.FunctionDef:
        arguments = [ast.arg(arg="self"), ast.arg(arg="other")]

        # elt = element I guess - but this is the terminology used in the
        # tuple AST function so elt it is.
        class_elts = []
        other_elts = []

        for field in self.resolved_field_list:
            if field.compare and not field.exclude_field:
                class_elts.append(field.ast_attribute())
                other_elts.append(field.ast_attribute("other"))

        if len(class_elts) > 0:
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
        return eq_func

    @property
    def iter_method(self) -> ast.FunctionDef:
        arguments = [ast.arg(arg="self")]

        body = [
            ast.Expr(value=ast.Yield(value=field.ast_attribute()))
            for field in self.resolved_field_list
            if not field.exclude_field
        ]

        if len(body) == 0:
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

        return iter_func

    @property
    def frozen_setattr_method(self) -> ast.FunctionDef:
        arguments = [ast.arg(arg="self"), ast.arg(arg="name"), ast.arg(arg="value")]
        args = ast.arguments(
            posonlyargs=[],
            args=arguments,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )

        fields_set = ast.Set(
            elts=[ast.Constant(value=name) for name in self.resolved_field_names]
        )

        test_conditions = [
            ast.Call(
                func=ast.Name(id="hasattr", ctx=ast.Load()),
                args=[
                    ast.Name(id="self", ctx=ast.Load()),
                    ast.Name(id="name", ctx=ast.Load()),
                ],
                keywords=[],
            ),
            ast.Compare(
                left=ast.Name(id="name", ctx=ast.Load()),
                ops=[ast.NotIn()],
                comparators=[fields_set],
            ),
        ]

        bool_test = ast.BoolOp(op=ast.Or(), values=test_conditions)

        if self.compile_slots:
            else_body = [
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="object", ctx=ast.Load()),
                            attr="__setattr__",
                            ctx=ast.Load(),
                        ),
                        args=[
                            ast.Name(id="self", ctx=ast.Load()),
                            ast.Name(id="name", ctx=ast.Load()),
                            ast.Name(id="value", ctx=ast.Load()),
                        ],
                        keywords=[],
                    )
                )
            ]
        else:
            assign = ast.Assign(
                targets=[
                    ast.Subscript(
                        value=ast.Attribute(
                            value=ast.Name(id="self", ctx=ast.Load()),
                            attr="__dict__",
                            ctx=ast.Load(),
                        ),
                        slice=ast.Name(id="name", ctx=ast.Load()),
                        ctx=ast.Store(),
                    )
                ],
                value=ast.Name(id="value", ctx=ast.Load()),
            )
            else_body = [assign]

        cond_body = [
            ast.Raise(
                exc=ast.Call(
                    func=ast.Name(id="TypeError", ctx=ast.Load()),
                    args=[
                        ast.Constant(
                            value=f"{self.name!r} object does not support attribute assignment"
                        )
                    ],
                    keywords=[],
                )
            ),
        ]

        body = [ast.If(test=bool_test, body=cond_body, orelse=else_body)]

        setattr_func = ast.FunctionDef(
            name="__setattr__",
            args=args,
            body=body,
            decorator_list=[],
            returns=None,
        )

        return setattr_func

    @property
    def frozen_delattr_method(self) -> ast.FunctionDef:
        arguments = [ast.arg(arg="self"), ast.arg(arg="name")]

        args = ast.arguments(
            posonlyargs=[],
            args=arguments,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        )

        body = [
            ast.Raise(
                exc=ast.Call(
                    func=ast.Name(id="TypeError", ctx=ast.Load()),
                    args=[
                        ast.Constant(
                            value=f"{self.name!r} object does not support attribute deletion"
                        )
                    ],
                    keywords=[],
                ),
            ),
        ]

        delattr_func = ast.FunctionDef(
            name="__delattr__",
            args=args,
            body=body,
            decorator_list=[],
            returns=None,
        )

        return delattr_func

    def generate_ast(self, prefabs: dict[str, "PrefabDetails"]) -> None:
        """
        Generate the prefab code and insert it into the body of the class.

        :param prefabs: Details on all prefabs in this module - for handling inheritance
        """

        # Handle inheritance
        self.resolve_inheritance(prefabs)

        # Remove values from the body
        for item in self.field_list:
            for assign in item.all_assignments:
                self.node.body.remove(assign)

        # Build body
        body = []
        if not self.compile_plain:
            body.append(self.compile_flag)
            body.append(self.fields_assignment)
            # body.append(self.internals_assignment)

        if self.compile_slots and "__slots__" not in self.defined_attr_names:
            body.append(self.slots_assignment)
        if self.match_args and "__match_args__" not in self.defined_attr_names:
            body.append(self.match_args_assignment)

        # Re-insert annotations
        for item in self.field_list:
            if item.ast_annassign:
                body.append(item.ast_annassign)

        if self._flag_kw_only is not None:
            self.node.body.remove(self._flag_kw_only)
            body.append(self._flag_kw_only)

        if (self.init and "__init__" not in self.defined_attr_names) or not self.init:
            body.append(self.init_method)
        if self.repr and "__repr__" not in self.defined_attr_names:
            body.append(self.repr_method)
        if self.eq and "__eq__" not in self.defined_attr_names:
            body.append(self.eq_method)
        if self.iter and "__iter__" not in self.defined_attr_names:
            body.append(self.iter_method)
        if self.frozen:
            body.append(self.frozen_setattr_method)
            body.append(self.frozen_delattr_method)

        # Add functions and definitions to the body
        # Remove the @prefab decorator
        # Check if a class starts with what we assume is a docstring.
        if (
            len(self.node.body) > 0
            and isinstance(self.node.body[0], ast.Expr)
            and isinstance(self.node.body[0].value, ast.Constant)
            and isinstance(self.node.body[0].value.value, str)
        ):
            self.node.body = self.node.body[0:1] + body + self.node.body[1:]
        else:
            # noinspection PyTypeChecker
            self.node.body = body + self.node.body
        self.node.decorator_list.remove(self.decorator)


class GatherClassAttrs(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.attrnames = set()  # set of attribute/function names - to help avoid re-assigning methods
        self.func_arguments: dict[str, dict[str, "None | ast.Expr"]] = dict()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.attrnames.add(node.name)
        args = node.args.args + node.args.kwonlyargs
        arguments = {item.arg: item.annotation for item in args}
        self.func_arguments[node.name] = arguments

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            self.attrnames.add(getattr(target, "id"))

    def visit_AnnAssign(self, node: ast.AnnAssign):
        if getattr(node, "value"):
            self.attrnames.add(getattr(node.target, "id"))


class GatherPrefabs(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.prefabs: dict[str, PrefabDetails] = {}
        self.dynamic_prefabs_present = False
        self.import_statements: list[ast.ImportFrom] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Looking for a call to DECORATOR_NAME with COMPILE_ARGUMENT == True
        # Check for plain classes, these will have the decorator removed and no fields defined
        prefab_decorator = None
        for item in node.decorator_list:
            if isinstance(item, ast.Name) and item.id == DECORATOR_NAME:
                self.dynamic_prefabs_present = True
            elif (
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
                else:
                    self.dynamic_prefabs_present = True

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

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "prefab_classes":
            as_imports = {item.name for item in node.names}
            if as_imports.issubset(prefab_essentials):
                self.import_statements.append(node)


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

    for p in prefabs.values():
        p.generate_ast(prefabs)

    if not gatherer.dynamic_prefabs_present:
        for item in gatherer.import_statements:
            tree.body.remove(item)

    ast.fix_missing_locations(tree)

    return tree
