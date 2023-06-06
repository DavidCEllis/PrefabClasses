# Differences with dataclasses #

While this project doesn't intend to exactly replicate other similar
modules it's worth noting where they differ in case users get tripped up.

Prefabs don't behave quite the same (externally) as dataclasses. They are
very different internally.

This doesn't include things that haven't been implemented, and only focuses
on intentional differences. Unintentional differences may be patched
or will be added to this list.

## Functional differences ##
1. prefabs do not generate the comparison methods other than `__eq__`
    * This could be added fairly easily but I don't use this feature so 
      it's not a priority.
1. the `as_dict` method in `prefab_classes` does *not* behave the same as 
   dataclasses' `asdict`
    * `as_dict` does *not* deepcopy the included fields, modification of mutable
      fields in the dictionary will modify them in the original object.
    * `as_dict` does *not* recurse
      - Recursion would require knowing how other objects should be serialized
      - dataclasses `asdict`'s recursion appears to be for handling json serialization
        prefab_classes provides a `to_json` function to assist with that.
1. dataclasses provides a `fields` function to access the underlying fields
    * Once a prefab class has been generated the underlying 'recipe' code is 
      removed as much as possible.
    * The 'compiled' form has no hidden attributes as they are replaced on compilation.
    * Prefab classes provide a `PREFAB_FIELDS` attribute with the field names
      in order.
    * The dynamic classes generate their code lazily so they need to keep the 
      'recipe' details around. `__prefab_internals__` contains this information.
1. Plain `attribute(...)` declarations can be used without the use of type hints.
    * If a plain assignment is used, all assignments **must** use `attribute`
1. Post init processing uses `__prefab_post_init__` instead of `__post_init__`
    * This is just a case of not wanting any confusion between the two.
    * `attrs` similarly does `__attrs_post_init__`
    * `__prefab_pre_init__` can also be used to define something to run
      before the body of `__init__`
    * If an attribute name is provided as an argument to either the pre_init
      or post_init functions the value will be passed through.
1. Unlike dataclasses, prefab classes will let you use unhashable default
   values.
    * This isn't to say that mutable defaults are a good idea in general but
      prefabs are supposed to behave like regular classes and regular classes
      let you make this mistake.
    * Usually you should use `attribute(default_factory=list)` or similar.
1. If `init` is `False` in `@prefab(init=False)` the method is still generated
   but renamed to `__prefab_init__`.
1. Slots are supported, but only in the compiled form.
    * The dynamic form has the same problems as `dataclasses` and `attrs` in that 
      in order to properly support slots it is necessary to create a new class
      and copy information over as it is impossible to add slots after the class
      is defined.
    * The compiled form modifies the class before it is defined so slots can
      easily be added.
1. InitVar annotations are not supported.
    * Passing arguments to `__prefab_post_init__` is done by adding the argument
      to the method signature.
    * Assignment is automatically skipped for any such values, default factories
      will be called and passed to the post init method.
    * To exclude such values from the fields list and other magic methods set
      `exclude_field=True` as an argument to `attribute`. Such attributes are
      required to be arguments to `__prefab_post_init__`.
1. The `__repr__` method for prefabs will have a different output if it will not `eval` correctly.
    * This isn't a guarantee that the regular `__repr__` will eval, but if it is known
      that the output would not `eval` then an alternative repr is used which does not
      look like it would `eval`.
1. default_factory functions will be called if `None` is passed as an argument
    * This makes it easier to wrap the function, but also doing anything else would 
      require an import for compiled classes which would break their import performance. 