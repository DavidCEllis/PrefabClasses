# Differences with dataclasses #

While this project doesn't intend to exactly replicate other similar
modules it's worth noting where they differ in case users get tripped up.

Prefabs don't behave quite the same (externally) as dataclasses. They are
very different internally.

This doesn't include things that haven't been implemented, and only focuses
on intentional differences. Unintentional differences may be patched
or will be added to this list.

## Functional differences ##
1. the `as_dict` method in `prefab_classes` does *not* recurse.
    * I don't think this is the correct behaviour to have by default.
    * A prefab may contain other prefabs that you might not want to serialize
      in the same way and so this shouldn't make that decision for you.
    * The case of JSON serialization with recursion (which some of the code in 
      dataclasses.todict seems to be written for) is handled by the to_json
      function provided.
2. dataclasses provides a `fields` function to access the underlying fields
    * Once a prefab class has been generated the underlying 'recipe' code is 
      removed as much as possible.
    * The 'compiled' form has no hidden attributes as they are replaced on compilation.
    * Prefab classes provide a `PREFAB_FIELDS` attribute with the field names
      in order.
    * The live/interpreted classes generate their code lazily so they need
      to keep the 'recipe' details around. `_attributes` and `_CLASSNAME_attributes`
      contain this information. The plain `_attributes` includes inherited values.
3. Allow the use of plain `attribute(...)` declarations without the use of
   type hints.
    * Typing is supposed to be optional so let it be optional.
4. Post init processing uses `__prefab_post_init__` instead of `__post_init__`
    * This is just a case of not wanting any confusion between the two.
    * `attrs` similarly does `__attrs_post_init__`
    * `__prefab_pre_init__` can also be used to define something to run
      before the body of `__init__`
5. Unlike dataclasses, prefab classes will let you use unhashable default
   values.
    * This isn't to say that mutable defaults are a good idea in general but
      prefabs are supposed to behave like regular classes and regular classes
      let you make this mistake.
    * Usually you should use `attribute(default_factory=list)` or similar.
6. If `init` is `False` in `@prefab(init=False)` the method is still generated
   but renamed to `__prefab_init__`.
7. Slots are supported, but only in the compiled form.
    * The live form has the same problems as `dataclasses` and `attrs` in that 
      in order to properly support slots it is necessary to create a new class
      and copy information over as it is impossible to add slots after the class
      is defined.
    * The compiled form modifies the class before it is defined so slots can
      easily be added.
8. InitVar annotations are not supported.
    * Passing arguments to `__prefab_post_init__` is done by adding the argument
      to the method signature.
    * Assignment is automatically skipped for any such values, default factories
      will be called and passed to the post init method.
    * To exclude such values from the fields list and other magic methods set
      `exclude_field=True` as an argument to `attribute`. Such attributes are
      required to be arguments to `__prefab_post_init__`.