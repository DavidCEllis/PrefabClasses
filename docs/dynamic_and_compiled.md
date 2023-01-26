# Differences between dynamic and compiled prefabs #

While effort has been put in to making dynamic and compiled prefabs
behave in the same way, there are some ways in which this is not possible.

Examples of usage can be seen in {doc}`basic_usage`

## Dynamic Prefabs ##

The dynamic method works roughly as *cluegen* worked, generating the 
required methods only when they are first accessed. This means that
modules should still import fairly quickly, but there is a performance
cost the first time any of the generated methods are used.

The advantage of these is more flexibility and that they will work and
be fairly fast in situations where compiling code to a .pyc is unavailable.
For example, `pyinstaller` generates the .pyc files directly, sidestepping
the import hook used to compile prefabs.

## Compiled Prefabs ##

The 'compiled' method instead generates all of the code when the 
module is first *compiled* into a .pyc file by modifying the AST. 

There are some additional things to be aware of when using the 
compiled method.

* The compiled method uses the **literal names** `prefab` and `attribute`
  to identify classes to be imported and to identify features. 
  If these are changed things will not work.
  * Technically the functions don't need to be imported, but even if they
    are the imports will be removed if no dynamic classes are generated
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
    * It would be possible to generate a class using the AST in this
      same way, but it is *much* slower than using templates and exec 
      at that point.
* In order to compile classes a `# COMPILE_PREFABS` comment must
  be at the top of a module. The module must also be imported in
  a `with prefab_compiler():` block.
    * This places an import hook that will compile prefabs in
      these files.
    * The comment is required as a fast way to identify that the
      module should be parsed into the AST and examined.
* Compiled classes support slots, dynamic classes do not.
    * While `attrs` supports this dynamically, it is forced to 
      make a new class and copy over features. This can have some
      side effects.
    * Compiled classes simply write in the `__slots__` field into the code.
