# Dynamic and Compiled Prefabs #

## Dynamic Prefab ##

The dynamic method works roughly as *cluegen* worked, generating the 
required methods only when they are first accessed. Compared to
attrs this trades speed of first access for speed of import. 
This also means that if a class method is never accessed then 
it is not generated.

Unlike cluegen this reverts to using a decorator for each class
rather than using inheritance. This is largely due to it being
much easier to identify a specific decorator in the AST to identify
classes to be modified for the compiled version.

## Compiled Prefabs ##

The 'compiled' method instead generates all of the code when the 
module is first *compiled* into a .pyc file by modifying the AST. 

There are some trade-offs and differences between the two.

* The compiled method uses the **literal names** `prefab` and `attribute`
  to identify classes to be imported and to identify features. 
  If these are changed things will not work.
  * The functions to not technically need to be imported however, unless
    the code should fallback to the dynamic method.
* After the .pyc files have been compiled, compiled classes import
  much more quickly than dynamic ones as they are plain python classes.
    * They are not *quite* as fast as modules with native classes,
      as hash-based invalidation is used instead of timestamp
      invalidation.
* Due to .pyc files being created independently inheritance is
  more restricted for compiled classes.
    * Inheritance across modules is not supported
    * Inheritance from non-prefab base classes is not supported
* As the classes must be compiled into the .pyc files, compiled
  classes can't be created interactively.
* In order to compile classes a `# COMPILE_PREFABS` comment must
  be at the top of a module. The module must also be imported in
  a `with prefab_compiler():` block.
    * This places an import hook that will compile prefabs in
      these files.
* Compiled classes support slots, dynamic classes do not.
    * While `attrs` supports this dynamically, it is forced to 
      make a new class and copy over features. This can have some
      side effects.