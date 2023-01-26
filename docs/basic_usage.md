# Getting Started #

Prefab Classes is designed to work much like dataclasses, using different
underlying methods. The basics should be familiar but there are some 
differences documented here: {doc}`extra/dataclasses_differences`.

The prefab_classes package provides two main functions in order to assist in
instructing the module on how you want your classes to be written.

The `@prefab` decorator instructs the module that the decorated class should
be rewritten with some options for which methods to generate. The `attribute`
function provides instructions for how to handle a specific field.

## Basic Usage ##

greeting.py
```python
from prefab_classes import prefab

@prefab
class Greeting:
    greeting: str = "Hello"
    
    def greet(self):
        print(f"{self.greeting} World!")
```

```python
>>> from greeting import Greeting
>>> hello = Greeting()
>>> hello.greet()
Hello World!

>>> hello
Greeting(greeting='Hello')

>>> hello.greeting
'Hello'

>>> goodbye = Greeting("Goodbye")
>>> hello == goodbye
False

>>> goodbye
Greeting(greeting='Goodbye')
```

