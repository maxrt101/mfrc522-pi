from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    OK = 0
    ERROR = 1
    NO_TAG_ERROR = 2
    TRANSCEIVE_ERROR = 3
    REQUEST_BAD_SIZE_ERROR = 4
    BAD_CRC_ERROR = 5
    ANTI_COLLISION_BAD_UID_SIZE_ERROR = 6
    SELECT_TAG_BAD_SIZE_ERROR = 7
    WRITE_BLOCK_BAD_SIZE_ERROR = 8
    WRITE_BLOCK_BAD_DATA_ERROR = 9


@dataclass
class TransceiveResult:
    status: Status
    data: list[int]
    size: int


@dataclass
class RequestResult:
    status: Status
    size: int


@dataclass
class AntiCollisionResult:
    status: Status
    uid: list[int]


@dataclass
class SelectTagResult:
    status: Status
    # TODO: Check if this is really the type
    tag_type: int

@dataclass
class ReadBlockResul:
    status: Status
    sector: int
    data: list[int]


@dataclass
class DumpResult:
    status: Status
    data: dict[int, list[int]]