import ast

from typing import Any, Union

from ..live import prefab

DECORATOR_NAME = 'prefab'
ATTRIBUTE_FUNCNAME = 'attribute'
FIELDS_ATTRIBUTE = 'PREFAB_FIELDS'
COMPILE_ARGUMENT = 'compile_prefab'
PLAIN_CLASS = 'compile_plain'
COMPILED_FLAG = 'COMPILED'

assignment_type = Union[ast.AnnAssign, ast.Assign]


class CodeGeneratorError(Exception):
    pass


# noinspection PyArgumentList
@prefab
class PrefabDetails:
    name: str
    node: ast.ClassDef
    fields: dict[str, "Field"]
    decorator: Any
    init_: bool = True
    repr_: bool = True
    eq_: bool = True
    iter_: bool = False
    plain_class: bool = False
    parents: Any = None


# noinspection PyArgumentList
@prefab
class Field:
    name: str
    field: Any
    default: Any = None
    default_factory: Any = None
    converter: Any = None
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

    @classmethod
    def from_keywords(cls, name, field, keywords, annotation=None):
        keys = {k.arg: k.value for k in keywords}
        default = keys.get("default", None)
        default_factory = keys.get("default_factory", None)
        converter = keys.get("converter", None)
        try:
            init_ = keys['init'].value
        except KeyError:
            init_ = True
        try:
            repr_ = keys['repr'].value
        except KeyError:
            repr_ = True
        try:
            kw_only = keys['kw_only'].value
        except KeyError:
            kw_only = False

        if default and default_factory:
            raise CodeGeneratorError("Cannot define both default and default_factory")

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
            attribute_func=True
        )


def discover_fields(class_node: ast.ClassDef) -> tuple[list[str], list[Field]]:
    def funcid_or_none(value):
        """get .func.id or return None"""
        return getattr(getattr(value, 'func', None), 'id', None)

    fields: list[Field] = []

    # If there are any plain assignments, annotated assignments that
    # do not use attribute() calls must be remove to match 'live'
    # behaviour.
    require_attribute_func = False

    for item in class_node.body:
        if isinstance(item, ast.AnnAssign):
            field_name = getattr(item.target, 'id')
            # Case that the value is an attribute() call
            if funcid_or_none(item.value) == ATTRIBUTE_FUNCNAME:
                field = Field.from_keywords(
                    name=field_name,
                    field=item,
                    keywords=item.value.keywords,
                    annotation=item.annotation,
                )
            else:
                field = Field(name=field_name, field=item, default=item.value, annotation=item.annotation)
            fields.append(field)
        elif (isinstance(item, ast.Assign)
              and len(item.targets) == 1
              and isinstance(item.value, ast.Call)):
            field_name = getattr(item.targets[0], 'id')
            field = Field.from_keywords(
                name=field_name,
                field=item,
                keywords=item.value.keywords
            )
            fields.append(field)
            require_attribute_func = True

    # Clear fields that are generated just by annotations
    if require_attribute_func:
        fields = [field for field in fields if field.attribute_func]

    # Clear the fields from he class_node body
    for item in fields:
        class_node.body.remove(item.field)

    field_names = [field.name for field in fields]

    return field_names, fields


def generate_fields(field_names: list[str]) -> ast.Assign:
    # generate and assign a list of fields for the class
    # PREFAB_FIELDS = ['x', 'y', 'z', ...]
    field_consts = [ast.Constant(value=name) for name in field_names]
    target = ast.Name(id=FIELDS_ATTRIBUTE, ctx=ast.Store())
    assignment = ast.Assign(targets=[target], value=ast.List(elts=field_consts, ctx=ast.Load()))
    return assignment


def generate_init(fields: list[Field]) -> ast.FunctionDef:
    """Build the AST for an INIT function"""

    posonlyargs = []  # Unused
    args = []
    kwonlyargs = []
    kw_defaults = []
    defaults = []

    body = []

    has_default = False

    self_target = ast.Name(id='self', ctx=ast.Load())
    args.append(ast.arg(arg='self'))

    for field in fields:
        # Skip if init_ is false
        if field.init_ is False:
            continue

        # Define the init signature
        assignment_value = ast.Name(id=field.name, ctx=ast.Load())
        if field.default or field.default_factory:
            # Include the annotation if this is an annotated value
            if hasattr(field, 'annotation'):
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
                        comparators=[ast.Constant(value=None)]
                    ),
                    body=ast.Name(id=field.name, ctx=ast.Load()),
                    orelse=field.default_factory_call
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
                raise CodeGeneratorError(
                    "Field without default defined after field with default."
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
                targets=[ast.Attribute(value=self_target, attr=field.name, ctx=ast.Store())],
                value=field.converter_call(assignment_value) if field.converter else assignment_value
            )
        )

    arguments = ast.arguments(
        posonlyargs=posonlyargs,
        args=args,
        kwonlyargs=kwonlyargs,
        kw_defaults=kw_defaults,
        defaults=defaults
    )

    init_func = ast.FunctionDef(
        name='__init__',
        args=arguments,
        body=body,
        decorator_list=[],
        returns=None
    )

    return init_func


def generate_repr(class_name: str, field_names: list[str]):

    arguments = [ast.arg(arg='self')]
    args = ast.arguments(
        posonlyargs=[],
        args=arguments,
        kwonlyargs=[],
        kw_defaults=[],
        defaults=[]
    )

    self_name = ast.Name(id='self', ctx=ast.Load())

    field_strings = [ast.Constant(value=f"{class_name}(")]
    for i, name in enumerate(field_names):
        if i > 0:
            field_strings.append(ast.Constant(value=', '))
        target = ast.Constant(value=f"{name}=")
        value = ast.FormattedValue(
            value=ast.Attribute(
                value=self_name,
                attr=f'{name}',
                ctx=ast.Load()
            ),
            conversion=114  # REPR formatting
        )
        field_strings.extend([target, value])

    field_strings.append(ast.Constant(value=")"))

    repr_string = ast.JoinedStr(values=field_strings)
    body = [ast.Return(value=repr_string)]

    repr_func = ast.FunctionDef(
        name='__repr__',
        args=args,
        body=body,
        decorator_list=[],
        returns=None
    )
    return repr_func


def generate_eq(field_names: list[str]) -> ast.FunctionDef:
    arguments = [ast.arg(arg='self'), ast.arg(arg='other')]

    class_elts = []
    other_elts = []

    for name in field_names:
        for obj_name, elt_list in [('self', class_elts), ('other', other_elts)]:
            elt_list.append(
                ast.Attribute(
                    value=ast.Name(id=obj_name, ctx=ast.Load()),
                    attr=name,
                    ctx=ast.Load()
                )
            )

    class_tuple = ast.Tuple(elts=class_elts, ctx=ast.Load())
    other_tuple = ast.Tuple(elts=other_elts, ctx=ast.Load())

    # (self.x, self.y, ...) == (other.x, other.y, ...)
    eq_comparison = ast.Compare(left=class_tuple, ops=[ast.Eq()], comparators=[other_tuple])

    # (self.x, ...) == (other.x, ...) if self.__class__ == other.__class__ else NotImplemented
    left_ifexp = ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__class__', ctx=ast.Load())
    right_ifexp = ast.Attribute(value=ast.Name(id='other', ctx=ast.Load()), attr='__class__', ctx=ast.Load())

    class_expr = ast.IfExp(
        test=ast.Compare(
            left=left_ifexp,
            ops=[ast.Eq()],
            comparators=[right_ifexp]
        ),
        body=eq_comparison,
        orelse=ast.Name(id='NotImplemented', ctx=ast.Load())
    )

    args = ast.arguments(
        posonlyargs=[],
        args=arguments,
        kwonlyargs=[],
        kw_defaults=[],
        defaults=[]
    )

    body = [ast.Return(value=class_expr)]

    eq_func = ast.FunctionDef(
        name='__eq__',
        args=args,
        body=body,
        decorator_list=[],
        returns=None
    )
    return eq_func


class TransformPrefab(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.prefabs = {}

    def visit_ClassDef(self, node: ast.ClassDef):
        # Looking for a call to DECORATOR_NAME with COMPILE_ARGUMENT == True
        # Check for plain classes, these will have the decorator removed and no fields defined
        prefab_decorator = None
        plain_class = False
        for item in node.decorator_list:
            if isinstance(item, ast.Call) and getattr(item.func, 'id') == DECORATOR_NAME:
                for keyword in item.keywords:
                    if keyword.arg == COMPILE_ARGUMENT and getattr(keyword.value, 'value') is True:
                        prefab_decorator = item
                    if keyword.arg == PLAIN_CLASS and getattr(keyword.value, 'value') is True:
                        plain_class = True
            if prefab_decorator:
                break

        if prefab_decorator:
            field_names, fields = discover_fields(node)

            if plain_class:
                node.decorator_list.remove(prefab_decorator)
            else:
                compiled_flag = ast.Assign(
                    targets=[ast.Name(id=COMPILED_FLAG, ctx=ast.Store())],
                    value=ast.Constant(value=True)
                )
                node.body.insert(0, compiled_flag)

                field_assignment = generate_fields(field_names)
                node.body.insert(1, field_assignment)

            node.body.append(generate_init(fields))

            node.body.append(generate_repr(node.name, field_names))

            node.body.append(generate_eq(field_names))

            ast.fix_missing_locations(node)

        return node


def generate_prefabs(source: str) -> ast.Module:
    """
    Generate the AST tree with the modified code for prefab classes

    :param source:
    :return:
    """
    tree = ast.parse(source)
    tranformer = TransformPrefab()
    tranformer.visit(tree)

    return tree
