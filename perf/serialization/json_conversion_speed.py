# This test looks at how quickly we can convert classes to JSON

import sys
import platform
from timeit import timeit

import json
import dataclasses
import attrs
import cattrs
from pydantic import BaseModel
import prefab_classes
from prefab_classes import prefab
from prefab_classes.funcs import to_json


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

    # Build JSON serializers
    plain_serializer = json.JSONEncoder()

    # Run all serialization once to build any caches for structure and to check equality
    dc_naive_json = plain_serializer.encode(dataclasses.asdict(dataclass_collection))
    attrs_naive_json = plain_serializer.encode(attrs.asdict(attrs_collection))
    cattrs_json = plain_serializer.encode(cattrs.unstructure(attrs_collection))
    pydantic_json = pydantic_collection.json()
    prefab_to_json = to_json(prefab_collection)

    # Assert they are all the same output
    outputs = [
        dc_naive_json,
        attrs_naive_json,
        cattrs_json,
        pydantic_json,
        prefab_to_json,
    ]

    base_out = json.loads(dc_naive_json)

    for i, op in enumerate(outputs[1:]):
        assert base_out == json.loads(op), f"{i}"

    print("| Method             | Time /s |")
    print("|--------------------|---------|")

    LOOPS = 50

    prefab_to_json_time = timeit(
        lambda: to_json(prefab_collection),
        number=LOOPS
    )
    print(f"| prefab_to_json     |     {prefab_to_json_time:.1f} |")

    dc_naive_time = timeit(
        lambda: plain_serializer.encode(dataclasses.asdict(dataclass_collection)),
        number=LOOPS,
    )
    print(f"| dataclasses_asdict |     {dc_naive_time:.1f} |")

    attrs_naive_time = timeit(
        lambda: plain_serializer.encode(attrs.asdict(attrs_collection)),
        number=LOOPS
    )
    print(f"| attrs_asdict       |     {attrs_naive_time:.1f} |")

    cattrs_time = timeit(
        lambda: plain_serializer.encode(cattrs.unstructure(attrs_collection)),
        number=LOOPS,
    )
    print(f"| cattrs             |     {cattrs_time:.1f} |")

    pydantic_time = timeit(
        lambda: pydantic_collection.json(),
        number=LOOPS
    )
    print(f"| pydantic           |     {pydantic_time:.1f} |")


if __name__ == "__main__":
    main()
