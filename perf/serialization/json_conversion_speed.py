# This test looks at how quickly we can convert classes to JSON

import sys
import platform
from timeit import timeit
import functools

import json
import dataclasses
import attrs
import cattrs
from pydantic import BaseModel
import prefab_classes
from prefab_classes import prefab
from prefab_classes.funcs import as_dict, to_json, _get_json_encoder


# Dataclasses Objects #
@dataclasses.dataclass
class DCMember:
    id: int
    active: bool


@dataclasses.dataclass
class DCObject:
    id: int
    name: str
    members: list[DCMember]


@dataclasses.dataclass
class DCCollection:
    group: list[DCObject]


# Attrs Versions
@attrs.define
class AttrMember:
    id: int
    active: bool


@attrs.define
class AttrObject:
    id: int
    name: str
    members: list[AttrMember]


@attrs.define
class AttrCollection:
    group: list[AttrObject]


# Pydantic Models
class PydanticMember(BaseModel):
    id: int
    active: bool


class PydanticObject(BaseModel):
    id: int
    name: str
    members: list[PydanticMember]


class PydanticCollection(BaseModel):
    group: list[PydanticObject]


# Prefab Classes
@prefab
class PrefabMember:
    id: int
    active: bool


@prefab
class PrefabObject:
    id: int
    name: str
    members: list[PrefabMember]


@prefab
class PrefabCollection:
    group: list[PrefabObject]


def main():
    print(f"Python Version: {sys.version}")
    print(f"Prefab Classes version: {prefab_classes.__version__}")
    print(f"Platform: {platform.platform()}")

    # Make the collections
    dataclass_collection = DCCollection(
        [
            DCObject(i, str(i) * 3, [DCMember(j, True) for j in range(0, 10)])
            for i in range(100000, 102000)
        ]
    )
    attrs_collection = AttrCollection(
        [
            AttrObject(i, str(i) * 3, [AttrMember(j, True) for j in range(0, 10)])
            for i in range(100000, 102000)
        ]
    )

    pydantic_collection = PydanticCollection(
        group=[
            PydanticObject(
                id=i,
                name=str(i) * 3,
                members=[PydanticMember(id=j, active=True) for j in range(0, 10)],
            )
            for i in range(100000, 102000)
        ]
    )

    prefab_collection = PrefabCollection(
        [
            PrefabObject(i, str(i) * 3, [PrefabMember(j, True) for j in range(0, 10)])
            for i in range(100000, 102000)
        ]
    )

    # Special faster method for dataclasses - from json_defaults.py
    @functools.lru_cache
    def field_default(fieldnames: tuple[str]):
        """
        Create a function that will take an object and return a {fieldname: obj.fieldname, ...}
        dictionary.

        (Fieldnames must be hashable so can not be a list.)

        :param fieldnames: tuple of fieldnames
        :return: dict conversion function
        """
        vals = ", ".join(f"'{fieldname}': o.{fieldname}" for fieldname in fieldnames)
        out_dict = f"{{{vals}}}"
        funcdef = (
            "def default(o):\n"
            "    try:\n"
            f"        return {out_dict}\n"
            "    except AttributeError:\n"
            "        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')\n"
        )
        globs = {}
        exec(funcdef, globs)
        method = globs["default"]
        return method

    @functools.lru_cache
    def _dc_defaultmaker(cls, exclude_fields: tuple[str] = ()):
        import dataclasses

        if not dataclasses.is_dataclass(cls):
            raise TypeError(f"Object of type {cls.__name__} is not JSON serializable")

        field_names = tuple(
            item.name
            for item in dataclasses.fields(cls)
            if item.name not in exclude_fields
        )

        method = field_default(field_names)
        return method

    def dataclass_default(o):
        """
        Function to provide to `json.dumps` to allow basic serialization
        of dataclass objects.
        """
        method = _dc_defaultmaker(type(o))
        return method(o)

    # Build JSON serializers
    plain_serializer = json.JSONEncoder()
    dc_cache_serializer = json.JSONEncoder(default=dataclass_default)
    prefab_serializer = json.JSONEncoder(default=as_dict)

    # Run all serialization once to build any caches for structure and to check equality
    dc_naive_json = plain_serializer.encode(dataclasses.asdict(dataclass_collection))
    dc_cache_json = dc_cache_serializer.encode(dataclass_collection)
    attrs_naive_json = plain_serializer.encode(attrs.asdict(attrs_collection))
    cattrs_json = plain_serializer.encode(cattrs.unstructure(attrs_collection))
    pydantic_json = pydantic_collection.json()
    prefab_asdict_json = prefab_serializer.encode(prefab_collection)
    prefab_to_json = to_json(prefab_collection)

    # Asser they are all the same output
    assert (
        dc_naive_json
        == dc_cache_json
        == attrs_naive_json
        == cattrs_json
        == pydantic_json
        == prefab_asdict_json
        == prefab_to_json
    )


    print("| Method            | Time /s |")
    print("|-------------------|---------|")

    LOOPS = 50
    prefab_time = timeit(
        lambda: prefab_serializer.encode(prefab_collection),
        number=LOOPS
    )
    print(f"| prefab_as_dict    |     {prefab_time:.1f} |")

    prefab_to_json_time = timeit(
        lambda: to_json(prefab_collection),
        number=LOOPS
    )
    print(f"| prefab_to_json    |     {prefab_to_json_time:.1f} |")

    dc_naive_time = timeit(
        lambda: plain_serializer.encode(dataclasses.asdict(dataclass_collection)),
        number=LOOPS,
    )
    print(f"| dataclasses_naive |     {dc_naive_time:.1f} |")

    dc_cache_time = timeit(
        lambda: dc_cache_serializer.encode(dataclass_collection),
        number=LOOPS
    )
    print(f"| dataclasses_cache |     {dc_cache_time:.1f} |")

    attrs_naive_time = timeit(
        lambda: plain_serializer.encode(attrs.asdict(attrs_collection)),
        number=LOOPS
    )
    print(f"| attrs_asdict      |     {attrs_naive_time:.1f} |")

    cattrs_time = timeit(
        lambda: plain_serializer.encode(cattrs.unstructure(attrs_collection)),
        number=LOOPS,
    )
    print(f"| cattrs            |     {cattrs_time:.1f} |")

    # pydantic_time = timeit(
    #     lambda: pydantic_collection.json(),
    #     number=LOOPS
    # )
    # print(f"| pydantic          |     {pydantic_time:.1f} |")


if __name__ == "__main__":
    main()
