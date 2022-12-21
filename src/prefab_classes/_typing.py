# Importing the typing module is slow
# However the dataclass_transform annotation is useful
# It's copied here

def dataclass_transform(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_specifiers: tuple = (),
    **kwargs,
):
    """Decorator that marks a function, class, or metaclass as providing
    dataclass-like behavior.
    Example usage with a decorator function:
        T = TypeVar("T")
        @dataclass_transform()
        def create_model(cls: type[T]) -> type[T]:
            ...
            return cls
        @create_model
        class CustomerModel:
            id: int
            name: str
    On a base class:
        @dataclass_transform()
        class ModelBase: ...
        class CustomerModel(ModelBase):
            id: int
            name: str
    On a metaclass:
        @dataclass_transform()
        class ModelMeta(type): ...
        class ModelBase(metaclass=ModelMeta): ...
        class CustomerModel(ModelBase):
            id: int
            name: str
    The ``CustomerModel`` classes defined above will
    be treated by type checkers similarly to classes created with
    ``@dataclasses.dataclass``.
    For example, type checkers will assume these classes have
    ``__init__`` methods that accept ``id`` and ``name``.
    The arguments to this decorator can be used to customize this behavior:
    - ``eq_default`` indicates whether the ``eq`` parameter is assumed to be
        ``True`` or ``False`` if it is omitted by the caller.
    - ``order_default`` indicates whether the ``order`` parameter is
        assumed to be True or False if it is omitted by the caller.
    - ``kw_only_default`` indicates whether the ``kw_only`` parameter is
        assumed to be True or False if it is omitted by the caller.
    - ``field_specifiers`` specifies a static list of supported classes
        or functions that describe fields, similar to ``dataclasses.field()``.
    - Arbitrary other keyword arguments are accepted in order to allow for
        possible future extensions.
    At runtime, this decorator records its arguments in the
    ``__dataclass_transform__`` attribute on the decorated object.
    It has no other runtime effect.
    See PEP 681 for more details.
    """
    def decorator(cls_or_fn):
        cls_or_fn.__dataclass_transform__ = {
            "eq_default": eq_default,
            "order_default": order_default,
            "kw_only_default": kw_only_default,
            "field_specifiers": field_specifiers,
            "kwargs": kwargs,
        }
        return cls_or_fn
    return decorator
