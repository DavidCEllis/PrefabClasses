import ast

from typing import Union

DECORATOR_NAME = 'prefab'
ATTRIBUTE_CLASSNAME = 'Attribute'
FIELDS_ATTRIBUTE = '_PREFAB_FIELDS'

assignment_type = Union[ast.AnnAssign, ast.Assign]


class CodeGeneratorError(Exception):
    pass


def discover_fields(class_node: ast.ClassDef) -> tuple[list[str], list[assignment_type]]:
    def funcid_or_none(value):
        """get .func.id or return None"""
        return getattr(getattr(value, 'func', None), 'id', None)

    fields: list[assignment_type] = []
    field_names: list[str] = []

    for item in class_node.body:
        if isinstance(item, ast.AnnAssign):
            fields.append(item)
            field_names.append(getattr(item.target, 'id'))
        elif isinstance(item, ast.Assign) and funcid_or_none(item.value):
            fields.append(item)
            field_names.append(getattr(item.targets[0], 'id'))

    # Clear the fields from he class_node body
    for item in fields:
        class_node.body.remove(item)

    return field_names, fields


def generate_fields(field_names: list[str]) -> ast.Assign:
    # generate and assign a list of fields for the class
    # _PREFAB_FIELDS = ['x', 'y', 'z', ...]
    field_consts = [ast.Constant(value=name) for name in field_names]
    target = ast.Name(id=FIELDS_ATTRIBUTE, ctx=ast.Store())
    assignment = ast.Assign(targets=[target], value=ast.List(elts=field_consts, ctx=ast.Load()))
    return assignment


def generate_init(fields: list[assignment_type]) -> ast.FunctionDef:
    """Build the AST for an INIT function"""

    posonlyargs = []  # Unused
    args = []
    kwonlyargs = []  # Unused
    kw_defaults = []  # Unused
    defaults = []

    body = []

    has_default = False

    self_target = ast.Name(id='self', ctx=ast.Load())
    args.append(ast.arg(arg='self'))

    for field in fields:
        # Define the init signature
        target = field.target if hasattr(field, 'target') else field.targets[0]
        assignment_value = ast.Name(id=target.id, ctx=ast.Load())
        if field.value:
            # Declare that there's a parameter with default value
            # in order to fail if there's one declared afterwards
            # This might not be necessary if it will fail later?
            has_default = True

            # Include the annotation if this is an annotated value
            if hasattr(field, 'annotation'):
                arg = ast.arg(arg=target.id, annotation=field.annotation)
            else:
                arg = ast.arg(arg=target.id)

            # For the body, defaults which are constant can be used
            # directly, potentially mutable defaults are instead
            # defined inside the body of the __init__ function,
            # guarded by an if expression
            if isinstance(field.value, ast.Constant):
                defaults.append(field.value)
            else:
                defaults.append(ast.Constant(value=None))
                assignment_value = ast.IfExp(
                    test=ast.Compare(
                        left=ast.Name(id=target.id, ctx=ast.Load()),
                        ops=[ast.IsNot()],
                        comparators=[ast.Constant(value=None)]
                    ),
                    body=ast.Name(id=target.id, ctx=ast.Load()),
                    orelse=field.value
                )
            args.append(arg)

        # Simpler code for values with no defaults
        else:
            if has_default:
                raise CodeGeneratorError(
                    "Field without default defined after field with default."
                )
            if field.annotation:
                arg = ast.arg(arg=target.id, annotation=field.annotation)
            else:
                arg = ast.arg(arg=target.id)
            args.append(arg)

        # Define the body
        body.append(
            ast.Assign(
                targets=[ast.Attribute(value=self_target, attr=target.id, ctx=ast.Store())],
                value=assignment_value
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
    def visit_ClassDef(self, node: ast.ClassDef):
        decorator_name = [item for item in node.decorator_list if item.id == DECORATOR_NAME]

        if decorator_name:
            node.decorator_list.remove(decorator_name[0])
            field_names, fields = discover_fields(node)

            field_assignment = generate_fields(field_names)
            node.body.insert(0, field_assignment)

            node.body.append(generate_init(fields))

            node.body.append(generate_repr(node.name, field_names))

            node.body.append(generate_eq(field_names))

            ast.fix_missing_locations(node)

        return node


def generate_prefabs(source):
    """
    Generate the AST tree with the modified code for prefab classes

    :param source:
    :return:
    """
    tree = ast.parse(source)
    TransformPrefab().visit(tree)

    return tree
