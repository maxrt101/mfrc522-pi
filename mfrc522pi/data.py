# Status (Error) and various Data Classes that represent the data returned by the API

from dataclasses import dataclass


@dataclass
class TransceiveResult:
    data: list[int]
    size: int


@dataclass
class RequestResult:
    size: int


@dataclass
class AntiCollisionResult:
    uid: list[int]


@dataclass
class SelectTagResult:
    # TODO: Check if this is really the type
    tag_type: int


@dataclass
class BlockData:
    sector: int
    data: list[int]


@dataclass
class BlocksData:
    data: dict[int, list[int]]
