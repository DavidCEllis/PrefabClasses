# API Autodocs #

## Core Functions ##

```{eval-rst}
.. autofunction:: prefab_classes::prefab
```

```{eval-rst}
.. autofunction:: prefab_classes::attribute
```

```{eval-rst}
.. autofunction:: prefab_classes::build_prefab
```

## Helper functions ##

```{eval-rst}
.. autofunction:: prefab_classes.funcs::is_prefab
.. autofunction:: prefab_classes.funcs::is_prefab_instance
.. autofunction:: prefab_classes.funcs::as_dict
.. autofunction:: prefab_classes.funcs::to_json
```

## Compilation functions ##

### Import hook handler ###

```{eval-rst}
.. autoclass:: prefab_classes.hook::prefab_compiler
.. autofunction:: prefab_classes.hook::insert_prefab_importhook
.. autofunction:: prefab_classes.hook::remove_prefab_importhook
```

### Previewer and .py unparser ###

These methods are not intended to be used in live code.
They are provided to be used either as a pre-processing 
function or as a tool to see how the class will be 
generated.

```{eval-rst}
.. autofunction:: prefab_classes.compiled::preview
.. autofunction:: prefab_classes.compiled::rewrite_to_py
.. autofunction:: prefab_classes.compiled::get_sources_to_compare
```
