# Welcome to Prefab Classes #

```{toctree}
---
maxdepth: 2
caption: "Contents:"
hidden: true
---
basic_usage
dynamic_construction
pre_post_init
why_not_dataclasses
extra/dataclasses_differences
extra/performance_tests
api
```

```{warning}
`prefab_classes` is being deprecated in favour of 
the prefab submodule of [ducktools-classbuilder](https://github.com/DavidCEllis/ducktools-classbuilder) 
which is a mostly compatible reimplementation.

This can be obtained using:

`python -m pip install ducktools-classbuilder`

The only (intentional) changes in that module are:
  * `SlotAttributes` is now `SlotFields`
  * `as_dict` is in the main module and does not cache
  * `@prefab(dict_method=True)` will create a cached as_dict 
    method on the class that the function will automatically 
    use.
  * attributes are excluded from `as_dict` using the `serialize` argument to `attribute`
  * `to_json` no longer exists - just use `json.dumps(obj, default=as_dict)`
```

Prefab Classes is a package that automatically generates basic class magic
methods so you don't have to write them yourself.

It turns this:

```python
from prefab_classes import prefab
from pathlib import Path
from typing import Union

@prefab
class Settings:
    output_file: Union[str, Path] = "path/to/settings.json"

    # Networking Settings
    hostname: str = "localhost"
    port: int = 12345
    # User Preferences
    font_size: int = 20
    font_color: str = "#000000"
    background_color: str = "#f1f8ff"

    def __prefab_post_init__(self, output_file):
        self.output_file: Path = Path(output_file)
```

Into this:

```python
from pathlib import Path
from typing import Union


class Settings:
    COMPILED = True
    PREFAB_FIELDS = [
        "output_file",
        "hostname",
        "port",
        "font_size",
        "font_color",
        "background_color",
    ]
    __match_args__ = (
        "output_file",
        "hostname",
        "port",
        "font_size",
        "font_color",
        "background_color",
    )

    def __init__(
        self,
        output_file: Union[str, Path] = "path/to/settings.json",
        hostname: str = "localhost",
        port: int = 12345,
        font_size: int = 20,
        font_color: str = "#000000",
        background_color: str = "#f1f8ff",
    ):
        self.hostname = hostname
        self.port = port
        self.font_size = font_size
        self.font_color = font_color
        self.background_color = background_color
        self.__prefab_post_init__(output_file=output_file)

    def __repr__(self):
        return f"{type(self).__qualname__}(output_file={self.output_file!r}, hostname={self.hostname!r}, port={self.port!r}, font_size={self.font_size!r}, font_color={self.font_color!r}, background_color={self.background_color!r})"

    def __eq__(self, other):
        return (
            (
                self.output_file,
                self.hostname,
                self.port,
                self.font_size,
                self.font_color,
                self.background_color,
            )
            == (
                other.output_file,
                other.hostname,
                other.port,
                other.font_size,
                other.font_color,
                other.background_color,
            )
            if self.__class__ == other.__class__
            else NotImplemented
        )

    def __prefab_post_init__(self, output_file):
        self.output_file: Path = Path(output_file)

```

You have probably seen something like this before if you've looked into the `dataclasses`
module or the `attrs` package. The main difference for `prefab_classes` is in the
implementation, although there are also some other design differences.

## Indices and tables ##
* {ref}`genindex`
* {ref}`search`