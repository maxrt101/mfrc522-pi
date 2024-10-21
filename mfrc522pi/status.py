# Status codes for the mfrc522pi library
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
    DATA_CORRUPTED_ERROR = 10
